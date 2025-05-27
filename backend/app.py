# backend/app.py
import os
import logging
import subprocess
import time
import json
import yaml
import mimetypes
import zipfile
from datetime import timedelta, datetime
# Import after_this_request and send_file
from flask import (Flask, request, jsonify, send_from_directory, url_for,
                   send_file, after_this_request) # Added after_this_request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
from dotenv import load_dotenv

# --- Boilerplate setup code remains the same ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(dotenv_path): load_dotenv(dotenv_path=dotenv_path)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CONTAINER_UPLOADS_PATH = '/app/uploads'; CONTAINER_OUTPUT_PATH = '/app/output'; SHARED_INFER_YAML_PATH = '/specs/infer.yaml'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'change-this-in-production-unsafe') # !! CHANGE THIS !!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))
app.config['UPLOAD_FOLDER'] = CONTAINER_UPLOADS_PATH; app.config['OUTPUT_FOLDER'] = CONTAINER_OUTPUT_PATH
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True); os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['OUTPUT_FOLDER'], "inference", "images_annotated"), exist_ok=True)
os.makedirs(os.path.dirname(SHARED_INFER_YAML_PATH), exist_ok=True)
app.logger.info(f"Upload: {app.config['UPLOAD_FOLDER']}, Output: {app.config['OUTPUT_FOLDER']}, Shared YAML: {SHARED_INFER_YAML_PATH}")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'zip'}
db = SQLAlchemy(app); jwt = JWTManager(app)
# --- Simplified CORS Configuration to Allow All Routes ---
allowed_origin = os.getenv('CORS_ORIGIN', 'http://localhost:3000')

# Apply CORS to the entire app, allowing the specific origin and supporting credentials
CORS(app, origins=allowed_origin, supports_credentials=True)
# This template is the source of truth. Only {username} will be replaced.
TRAIN_YAML_TEMPLATE = """train:
  num_gpus: 1
  num_nodes: 1
  validation_interval: 1
  optim:
    lr_backbone: 2e-05
    lr: 0.0002
    lr_steps: [10, 20]
    momentum: 0.9
  num_epochs: 2
  freeze: ["backbone", "bert"]
  pretrained_model_path: /pre_trained_models/grounding_dino_swin_tiny_commercial_trainable.pth
  precision: bf16
  activation_checkpoint: True
dataset:
  train_data_sources:
    - image_dir: /data/finetune_datasets/{username}/coco/train/
      json_file: /data/finetune_datasets/{username}/odvg/annotations/train_odvg.jsonl
      label_map: /data/finetune_datasets/{username}/odvg/annotations/train_odvg_labelmap.json
  val_data_sources:
    image_dir: /data/finetune_datasets/{username}/coco/val/
    json_file: /data/finetune_datasets/{username}/odvg/annotations/val_remapped.json
  max_labels: 80
  batch_size: 1
  workers: 1
model:
  backbone: swin_tiny_224_1k
  num_feature_levels: 4
  dec_layers: 6
  enc_layers: 6
  num_queries: 900
  dropout_ratio: 0.0
  dim_feedforward: 2048
  loss_types: ['labels', 'boxes', 'masks']
  log_scale: auto
  class_embed_bias: True
"""
app.logger.info(f"CORS configured for origin(s): {allowed_origin}")
# --- End Boilerplate ---

# --- Database Models ---
# (Keep User and UploadedImage models exactly as before)
class User(db.Model):
    __tablename__ = 'users'; id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(80), unique=True, nullable=False); email = db.Column(db.String(120), unique=True, nullable=False); password_hash = db.Column(db.String(256), nullable=False); images = db.relationship('UploadedImage', backref='uploader', lazy=True, cascade="all, delete-orphan")
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def __repr__(self): return f'<User {self.username}>'
class UploadedImage(db.Model):
    __tablename__ = 'uploaded_images'; id = db.Column(db.Integer, primary_key=True); filename = db.Column(db.String(256), nullable=False); keywords = db.Column(db.Text, nullable=True); upload_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow); user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False); processed_image_path = db.Column(db.String(512), nullable=True)
    def __repr__(self): return f'<UploadedImage ID {self.id} - {self.filename}>'

# --- Create Database Tables ---
with app.app_context():
    try: db.create_all(); app.logger.info("DB tables checked/created.")
    except Exception as e: app.logger.error(f"Error creating DB tables: {e}", exc_info=True)

# --- Helper Functions ---
def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# --- Helper function to update train.yaml ---
def update_train_yaml(username):
    """
    Updates the train.yaml file by replacing only the {username} placeholders
    in the TRAIN_YAML_TEMPLATE.
    The paths in the template are from the perspective of the TAO training container.
    """
    app.logger.info(f"[update_train_yaml] Called for user: {username}")

    base_specs_path_in_container = os.path.dirname(SHARED_INFER_YAML_PATH) # Should be '/specs'
    absolute_train_yaml_path = os.path.join(base_specs_path_in_container, 'train.yaml') # Should be '/specs/train.yaml'
    
    app.logger.info(f"[update_train_yaml] Target train.yaml path set to: '{absolute_train_yaml_path}'")

    try:
        # This is the crucial step: only substitutes {username} in the template string.
        # The rest of the TRAIN_YAML_TEMPLATE string remains unchanged by this operation.
        modified_yaml_content_str = TRAIN_YAML_TEMPLATE.format(username=username)
        
        # Validate the resulting YAML string and get a Python dictionary.
        # This step does not change the content derived from the template, only parses it.
        try:
            yaml_data = yaml.safe_load(modified_yaml_content_str)
        except yaml.YAMLError as ye:
            app.logger.error(f"[update_train_yaml] Invalid YAML generated from template for user {username} after .format(): {ye}", exc_info=True)
            app.logger.debug(f"Problematic YAML string content:\n{modified_yaml_content_str}")
            return False

        app.logger.info(f"[update_train_yaml] Attempting to write to train.yaml at: '{absolute_train_yaml_path}'")
        # Write the validated data to the YAML file.
        # yaml.dump serializes the Python dictionary back to YAML format.
        # With default_flow_style=False and sort_keys=False, it respects the original structure and order
        # as much as possible. It does not alter the data values themselves.
        with open(absolute_train_yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
            
        app.logger.info(f"[update_train_yaml] Successfully updated train.yaml for user {username} at '{absolute_train_yaml_path}'")
        return True
        
    except FileNotFoundError: # Should be rare if /specs exists and permissions are okay
        app.logger.error(f"[update_train_yaml] FileNotFoundError: Could not open/write train.yaml at '{absolute_train_yaml_path}'. Check '/specs' directory.", exc_info=True)
        return False
    except PermissionError as pe:
        app.logger.error(f"[update_train_yaml] PermissionError writing to train.yaml at '{absolute_train_yaml_path}': {pe}", exc_info=True)
        return False
    except Exception as e: # Catches other errors, like .format() if placeholder is missing, though less likely with {username}
        app.logger.error(f"[update_train_yaml] Generic error updating train.yaml for user {username} at path '{absolute_train_yaml_path}': {str(e)}", exc_info=True)
        return False
# --- NEW: Cleanup Helper Function ---
def cleanup_files(paths_to_delete):
    """Safely attempts to delete a list of files after the request."""
    # This runs outside the original request context but within the app context
    # managed by Flask when using after_this_request
    with app.app_context():
        app.logger.debug(f"Executing scheduled cleanup for paths: {paths_to_delete}")
        for file_path in paths_to_delete:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    app.logger.info(f"(Cleanup) Successfully deleted: {file_path}")
                except OSError as e:
                    app.logger.error(f"(Cleanup) Error deleting file {file_path}: {e}")
            else:
                app.logger.warning(f"(Cleanup) Skipped, file not found or path empty: {file_path}")


# --- API Routes ---

@app.route('/api/upload_image', methods=['POST'])
@jwt_required()
def upload_and_process_image():
    """
    UNSAFE VERSION: Handles upload, OVERWRITES shared
    infer.yaml, triggers direct
    TAO command, updates DB, returns processed IMAGE DATA.
    Schedules cleanup of ONLY the INPUT file AFTER response is sent.
    WARNING: RACE CONDITIONS WILL OCCUR WITH CONCURRENT REQUESTS (YAML Overwrite).
    """
    # --- Keep User Lookup, Input Validation, Filename generation, Path calculations ---
    # (These sections remain the same)
    current_user_username = get_jwt_identity()
    user = db.session.scalar(db.select(User).filter_by(username=current_user_username))
    if not user: return jsonify({"message": "User not found"}), 404
    if 'image' not in request.files: return jsonify({"message": "No 'image' file part"}), 400
    file = request.files['image']
    keywords_str = request.form.get('keywords', '')
    color_map_json_str = request.form.get('color_map', '{}')
    if file.filename == '': return jsonify({"message": "No image selected"}), 400
    if not allowed_file(file.filename): return jsonify({"message": "File type not allowed"}), 400
    if not keywords_str.strip(): return jsonify({"message": "Keywords/Captions cannot be empty"}), 400
    try:
        color_map_dict = json.loads(color_map_json_str)
        if not isinstance(color_map_dict, dict): raise ValueError("Color map must be JSON object.")
        captions_list = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        if not captions_list: raise ValueError("Keywords/Captions cannot result in an empty list.")
        assert isinstance(captions_list, list)
    except json.JSONDecodeError: return jsonify({"message": "Invalid JSON format for color_map."}), 400
    except ValueError as ve: return jsonify({"message": str(ve)}), 400
    except AssertionError: return jsonify({"message": "Internal error preparing captions list."}), 500
    io_filename = secure_filename(file.filename)
    app.logger.info(f"Processing upload, using filename: '{io_filename}'")
    filepath_input_img_backend = os.path.join(app.config['UPLOAD_FOLDER'], io_filename)
    shared_yaml_path_backend = SHARED_INFER_YAML_PATH
    output_subdir = os.path.join("inference", "images_annotated")
    output_filename = io_filename
    relative_output_path = os.path.join(output_subdir, output_filename)
    filepath_output_img_backend = os.path.join(app.config['OUTPUT_FOLDER'], relative_output_path)
    shared_yaml_path_inference = "/specs/infer.yaml"
    checkpoint_path_inference = "/pre_trained_models/model_epoch_049.pth"
    app.logger.info(f"Input image path (backend): {filepath_input_img_backend}")
    app.logger.info(f"Expecting output file at (backend): {filepath_output_img_backend}")

    new_image_record = None
    yaml_written = False
    # --- Define file path for input cleanup in finally/after_request block ---
    input_file_to_cleanup = filepath_input_img_backend
    # Output file is NOT cleaned up in this version

    try:
        # 1. Save input image file
        # ... (Save file code as before) ...
        os.makedirs(os.path.dirname(filepath_input_img_backend), exist_ok=True)
        file.save(filepath_input_img_backend)
        app.logger.info(f"Saved input image to: {filepath_input_img_backend}")

        # 2. Create initial DB record
        # ... (DB record code as before) ...
        new_image_record = UploadedImage(filename=io_filename, keywords=keywords_str, user_id=user.id)
        db.session.add(new_image_record)
        db.session.flush(); image_id = new_image_record.id
        app.logger.info(f"DB record initialized for image ID {image_id}")

        # 3. Generate Dynamic YAML Content
        # ... (YAML generation as before) ...
        yaml_config = {
            'inference': { 'conf_threshold': 0.5, 'color_map': color_map_dict },
            'dataset': { 'infer_data_sources': { 'image_dir': ['/data'], 'captions': captions_list }, 'batch_size': 1, 'workers': 1 },
            'model': { 'backbone': 'swin_tiny_224_1k', 'num_feature_levels': 4, 'dec_layers': 6, 'enc_layers': 6, 'num_queries': 900, 'dropout_ratio': 0.0, 'dim_feedforward': 2048, 'loss_types': ['labels', 'boxes', 'masks'], 'log_scale': 'auto', 'class_embed_bias': True }
        }

        # 4. !!! UNSAFE STEP: Overwrite shared YAML file !!!
        # ... (YAML overwrite code as before) ...
        try:
            with open(shared_yaml_path_backend, 'w') as yaml_file:
                yaml.dump(yaml_config, yaml_file, default_flow_style=False, sort_keys=False)
            yaml_written = True; app.logger.warning(f"UNSAFE: Overwrote shared config file: {shared_yaml_path_backend}")
        except Exception as yaml_err: app.logger.error(f"Failed to overwrite YAML: {yaml_err}", exc_info=True); raise

        # 5. Construct the EXACT Docker Exec Command
        # ... (Command construction as before) ...
        command = [ "docker", "exec", "inference", "mask_grounding_dino", "inference", "-e", shared_yaml_path_inference, "inference.checkpoint=" + checkpoint_path_inference ]
        app.logger.info(f"Executing command for image ID {image_id}: {' '.join(command)}")

        # 6. Execute command
        # ... (Subprocess execution as before) ...
        timeout_seconds = 300
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout_seconds)

        # 7. Process Result
        if process.returncode == 0:
            app.logger.info(f"TAO command finished for image ID {image_id} (RC=0).")
            # Verify output file exists at the CORRECT path
            if os.path.exists(filepath_output_img_backend):
                app.logger.info(f"Output file verified at: {filepath_output_img_backend}")
                # Update DB
                new_image_record.processed_image_path = relative_output_path
                db.session.commit()
                app.logger.info(f"DB record {image_id} updated and committed.")

                # --- Schedule INPUT file cleanup and Prepare Response ---
                mimetype = mimetypes.guess_type(filepath_output_img_backend)[0] or 'application/octet-stream'
                app.logger.info(f"Preparing to send result file {filepath_output_img_backend} with mimetype {mimetype}")

                # Define ONLY the input file path for cleanup after this request
                files_to_delete_later = [input_file_to_cleanup]

                # This wrapper function is needed because after_this_request passes the response object
                def cleanup_task(response):
                    cleanup_files(files_to_delete_later)
                    return response # Must return the response object

                after_this_request(cleanup_task) # Schedule the cleanup
                app.logger.info(f"Scheduled cleanup for input file: {input_file_to_cleanup}")

                # Send the image file back directly
                response = send_file(filepath_output_img_backend, mimetype=mimetype, as_attachment=False)
                return response # Return file data

            else: # Command finished OK but output file missing
                app.logger.error(f"TAO command OK but output file NOT FOUND at: {filepath_output_img_backend}")
                db.session.rollback()
                app.logger.error(f"TAO stderr (check errors):\n{process.stderr}")
                # Clean up input file immediately on this specific failure path? Optional.
                if os.path.exists(input_file_to_cleanup): os.remove(input_file_to_cleanup)
                return jsonify({"message": "Processing failed: Output file not found after inference."}), 500
        else: # Command failed
            app.logger.error(f"TAO command failed (code: {process.returncode})")
            app.logger.error(f"TAO stderr:\n{process.stderr}")
            db.session.rollback()
            # Clean up input file immediately on inference failure? Optional.
            if os.path.exists(input_file_to_cleanup): os.remove(input_file_to_cleanup)
            return jsonify({"message": f"Processing failed: TAO inference error (code: {process.returncode})."}), 500

    # --- Exception Handling ---
    # Remove cleanup from here, rely on scheduled cleanup or manual for now on errors
    except subprocess.TimeoutExpired:
        app.logger.error(f"TAO command timed out (image: {io_filename})"); db.session.rollback()
        # if os.path.exists(input_file_to_cleanup): os.remove(input_file_to_cleanup) # Optional: Cleanup input on timeout
        return jsonify({"message": "Processing failed: Inference timed out."}), 504
    except FileNotFoundError as e:
         app.logger.error(f"File system or command error: {e}", exc_info=True); db.session.rollback()
         # if os.path.exists(input_file_to_cleanup): os.remove(input_file_to_cleanup) # Optional: Cleanup input on error
         return jsonify({"message": "Server configuration or file system error."}), 500
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Unhandled error: {e}", exc_info=True)
        # if os.path.exists(input_file_to_cleanup): os.remove(input_file_to_cleanup) # Optional: Cleanup input on error
        return jsonify({"message": "An unexpected server error occurred."}), 500

    # --- Finally Block ---
    finally:
        # No file deletions happen here anymore. Cleanup is scheduled on success path only.
        app.logger.debug(f"Request processing finished for image: {io_filename}.")
        pass


@app.route('/api/finetune', methods=['POST'])
@jwt_required()
def finetune_upload():
    """
    Accepts a .zip dataset file and extracts it directly in the user's folder,
    replacing any existing dataset.
    """
    current_user_username = get_jwt_identity()
    user = db.session.scalar(db.select(User).filter_by(username=current_user_username))
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'dataset' not in request.files:
        return jsonify({'error': 'No dataset file provided'}), 400
    file = request.files['dataset']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'zip'):
        return jsonify({'error': 'File type not allowed. Please upload a .zip file'}), 400

    # Create user directory with username
    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'finetune_datasets', user.username)
    
    # Remove any existing dataset folder and its contents
    if os.path.exists(user_dir):
        app.logger.info(f"Removing existing dataset for user {user.username}")
        try:
            import shutil
            shutil.rmtree(user_dir)
        except PermissionError as e:
            app.logger.error(f"Permission error when removing directory: {str(e)}")
            return jsonify({'error': 'Permission error: Could not replace existing dataset. Please contact administrator.'}), 500
        except Exception as e:
            app.logger.error(f"Error removing directory: {str(e)}")
            return jsonify({'error': f'Failed to prepare for new dataset: {str(e)}'}), 500
    
    # Create fresh directory
    try:
        os.makedirs(user_dir, exist_ok=True)
    except PermissionError as e:
        app.logger.error(f"Permission error when creating directory: {str(e)}")
        return jsonify({'error': 'Permission error: Could not create dataset directory. Please contact administrator.'}), 500
    except Exception as e:
        app.logger.error(f"Error creating directory: {str(e)}")
        return jsonify({'error': f'Failed to create dataset directory: {str(e)}'}), 500
    
    # Save zip file temporarily with the name 'data.zip'
    temp_zip_path = os.path.join(user_dir, "data.zip")
    file.save(temp_zip_path)

    # Unzip directly into the user directory
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            extract_temp_dir = os.path.join(user_dir, "temp_extracted")
            os.makedirs(extract_temp_dir, exist_ok=True)
            zip_ref.extractall(extract_temp_dir)

        # Rename extracted folder to 'coco'
        extracted_content = os.listdir(extract_temp_dir)
        if len(extracted_content) == 1 and os.path.isdir(os.path.join(extract_temp_dir, extracted_content[0])):
            os.rename(os.path.join(extract_temp_dir, extracted_content[0]), os.path.join(user_dir, "coco"))
        else:
            os.rename(extract_temp_dir, os.path.join(user_dir, "coco"))
        os.remove(temp_zip_path)
    except PermissionError as e:
        app.logger.error(f"Permission error: {str(e)}")
        return jsonify({'error': f'Permission error: Could not extract dataset. Please contact administrator.'}), 500
    except Exception as e:
        app.logger.error(f"Error extracting dataset: {str(e)}")
        return jsonify({'error': f'Failed to unzip dataset: {str(e)}'}), 500

    # --- NEW: Update convert.yaml after dataset upload ---
    update_success = update_convert_yaml(user.username)
    if not update_success:
        return jsonify({'error': 'Failed to update dataset configuration. Upload succeeded, but configuration update failed.'}), 500

    # --- NEW: Execute TAO dataset conversion command ---
    app.logger.info(f"Attempting to convert dataset for user {user.username} using TAO.")
    
    # Construct the TAO command
    # Paths are from the perspective of the 'inference' container
    # /specs/convert.yaml is the path inside the inference container
    # /data/... maps to the host's app.config['UPLOAD_FOLDER']/...
    spec_file_path_in_container = os.path.join(os.path.dirname(SHARED_INFER_YAML_PATH), 'convert.yaml') # Should be /specs/convert.yaml
    
    # These paths are relative to the /data mount inside the inference container
    coco_ann_file_param = f"coco.ann_file=/data/finetune_datasets/{user.username}/coco/annotations/train.json"
    results_dir_param = f"results_dir=/data/finetune_datasets/{user.username}/odvg/annotations/"

    # Command structure: docker exec <container_name> <executable> <sub_commands/args...>
    # Similar to: docker exec inference mask_grounding_dino inference -e /specs/infer.yaml ...
    tao_convert_command = [
        "docker", "exec", "data_services",  # Target container
        "annotations", "convert",  # TAO command and subcommands
        "-e", spec_file_path_in_container,  # Spec file argument
        coco_ann_file_param,                # COCO annotation file parameter
        results_dir_param                   # Results directory parameter
    ]

    app.logger.info(f"Executing TAO dataset conversion command for user {user.username}: {' '.join(tao_convert_command)}")
    
    try:
        timeout_seconds = 300  # Adjust as needed
        process = subprocess.run(tao_convert_command, capture_output=True, text=True, check=False, timeout=timeout_seconds)

        if process.returncode == 0:
            app.logger.info(f"TAO dataset conversion successful for user {user.username} (train.json).")
            app.logger.info(f"TAO conversion (train.json) stdout:\\n{process.stdout}")

            # --- NEW: Execute TAO dataset conversion command for validation set ---
            app.logger.info(f"Attempting to convert validation dataset for user {user.username} using TAO.")
            
            coco_val_ann_file_param = f"coco.ann_file=/data/finetune_datasets/{user.username}/coco/annotations/val.json"
            # results_dir_param is the same as before
            # spec_file_path_in_container is the same as before

            tao_val_convert_command = [
                "docker", "exec", "data_services",      # Target container
                "annotations", "convert",  # TAO command and subcommands
                "-e", spec_file_path_in_container,  # Spec file argument
                coco_val_ann_file_param,            # COCO val annotation file
                results_dir_param,                  # Results directory (same)
                "data.output_format=COCO",
                "coco.use_all_categories=True"
            ];

            app.logger.info(f"Executing TAO validation dataset conversion command for user {user.username}: {' '.join(tao_val_convert_command)}")
            
            try:
                val_process = subprocess.run(tao_val_convert_command, capture_output=True, text=True, check=False, timeout=timeout_seconds)

                if val_process.returncode == 0:
                    app.logger.info(f"TAO validation dataset conversion successful for user {user.username} (val.json).")
                    app.logger.info(f"TAO validation conversion stdout:\\n{val_process.stdout}")
                    # Both conversions successful
                else:
                    app.logger.error(f"TAO validation dataset conversion failed for user {user.username} (RC={val_process.returncode}).")
                    app.logger.error(f"TAO validation conversion stderr:\\n{val_process.stderr}")
                    app.logger.error(f"TAO validation conversion stdout:\\n{val_process.stdout}")
                    return jsonify({
                        'error': f'Training dataset converted, but validation dataset conversion failed (TAO RC={val_process.returncode}). Check server logs.'
                    }), 500
            
            except subprocess.TimeoutExpired:
                app.logger.error(f"TAO validation dataset conversion timed out for user {user.username}.")
                return jsonify({'error': 'Validation dataset conversion process timed out.'}), 504
            except Exception as e_val:
                app.logger.error(f"An unexpected error occurred during TAO validation dataset conversion for user {user.username}: {str(e_val)}", exc_info=True)
                return jsonify({'error': f'An unexpected error occurred during validation dataset conversion: {str(e_val)}'}), 500
            # --- End of NEW validation set conversion ---

        else:
            app.logger.error(f"TAO dataset conversion failed for user {user.username} (RC={process.returncode}).")
            app.logger.error(f"TAO conversion stderr:\\n{process.stderr}")
            app.logger.error(f"TAO conversion stdout:\\n{process.stdout}")
            return jsonify({
                'error': f'Dataset uploaded and extracted, but dataset conversion failed (TAO RC={process.returncode}). Check server logs for details.'
            }), 500
            
    except subprocess.TimeoutExpired:
        app.logger.error(f"TAO dataset conversion timed out for user {user.username}.")
        return jsonify({'error': 'Dataset conversion process timed out.'}), 504
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during TAO dataset conversion for user {user.username}: {str(e)}", exc_info=True)
        return jsonify({'error': f'An unexpected error occurred during dataset conversion: {str(e)}'}), 500
    app.logger.info(f"Executing TAO TRAINING command for user {user.username}: {' '.join(tao_convert_command)}")
    try:
        tao_train_command = [
        "docker", "exec", "inference",
        "mask_grounding_dino", "train",
        "-e", "/specs/train.yaml",
        "train.num_gpus=1",
        f"results_dir=/results/finetune"
        ]
        timeout_seconds = 300  # Adjust as needed
        process = subprocess.run(tao_train_command, capture_output=True, text=True, check=False, timeout=timeout_seconds)

        if process.returncode == 0:
            app.logger.info(f"TAO training command successful for user {user.username} (train.json).")
            app.logger.info(f"TAO training (train.json) stdout:\\n{process.stdout}")
            app.logger.info(f"Executing TAO validation dataset conversion command for user {user.username}: {' '.join(tao_val_convert_command)}")
            
            try:
                val_process = subprocess.run(tao_train_command, capture_output=True, text=True, check=False, timeout=timeout_seconds)

                if val_process.returncode == 0:
                    app.logger.info(f"TAO train command  successful for user {user.username} (val.json).")
                    app.logger.info(f"TAO train command stdout:\\n{val_process.stdout}")
                    # Both conversions successful
                else:
                    app.logger.error(f"TAO train command conversion failed for user {user.username} (RC={val_process.returncode}).")
                    app.logger.error(f"TAO train command stderr:\\n{val_process.stderr}")
                    app.logger.error(f"TAO train command stdout:\\n{val_process.stdout}")
                    return jsonify({
                        'error': f'error'
                    }), 500
            
            except subprocess.TimeoutExpired:
                app.logger.error(f"error")
                return jsonify({'error'}), 504
            except Exception as e_val:
                app.logger.error(f"An unexpected error occurred during TAO training for user {user.username}: {str(e_val)}", exc_info=True)
                return jsonify({'error': f'An unexpected error occurred during training  conversion: {str(e_val)}'}), 500
            # --- End of NEW validation set conversion ---

        else:
            app.logger.error(f"TAO training  failed for user {user.username} (RC={process.returncode}).")
            app.logger.error(f"TAO training stderr:\\n{process.stderr}")
            app.logger.error(f"TAO training stdout:\\n{process.stdout}")
            return jsonify({
                'error': f'traininig error'
            }), 500
            
    except subprocess.TimeoutExpired:
        app.logger.error(f"TAO dataset conversion timed out for user {user.username}.")
        return jsonify({'error': 'Dataset conversion process timed out.'}), 504
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during TAO dataset conversion for user {user.username}: {str(e)}", exc_info=True)
        return jsonify({'error': f'An unexpected error occurred during dataset conversion: {str(e)}'}), 500
    return jsonify({
        'message': 'Dataset uploaded, extracted, and converted successfully',
        'dataset_id': user.username,
        'extract_dir': user_dir
    }), 200

@app.route('/api/finetune/status/<dataset_id>', methods=['GET'])
@jwt_required()
def get_finetune_status(dataset_id):
    """
    Get the status of a fine-tuning process
    """
    current_user_username = get_jwt_identity()
    user = db.session.scalar(db.select(User).filter_by(username=current_user_username))
    
    try:
        user_id = dataset_id.split('_')[0]
        if str(user.id) != user_id:
            return jsonify({'error': 'Unauthorized access to dataset status'}), 403
            
        # TODO: Implement actual status checking
        # For now, return a mock status
        return jsonify({
            'dataset_id': dataset_id,
            'status': 'pending',
            'progress': 0,
            'message': 'Fine-tuning process queued'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error checking fine-tune status: {str(e)}")
        return jsonify({'error': 'Error checking fine-tune status'}), 500


# --- Other Routes (/api/results, /api/health, /api/register, /api/login, /api/protected) ---
# Keep these exactly as before.
@app.route('/api/results/<path:subpath>')
@jwt_required()
def serve_processed_image(subpath):
    # ... (same implementation) ...
    app.logger.info(f"Attempting to serve result file: {subpath} from {app.config['OUTPUT_FOLDER']}")
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], subpath)
    if not os.path.isfile(file_path): return jsonify({"message": "Result file not found."}), 404
    return send_from_directory(app.config['OUTPUT_FOLDER'], subpath)

@app.route('/api/health', methods=['GET'])
def health_check():
    # ... (same implementation) ...
    db_status = "connected";
    try: db.session.execute(db.text('SELECT 1'))
    except Exception as e: db_status = f"error: {e}"
    return jsonify({"status": "healthy", "database": db_status, "timestamp": datetime.utcnow().isoformat()}), 200

@app.route('/api/register', methods=['POST'])
def register():
    # ... (same implementation) ...
    data = request.get_json();
    if not data or not data.get('username') or not data.get('password') or not data.get('email'): return jsonify({"message": "Missing fields"}), 400
    username, email, password = data['username'], data['email'], data['password']
    user_exists = db.session.query(User.id).filter((User.username == username) | (User.email == email)).limit(1).scalar() is not None
    if user_exists: return jsonify({"message": "Username or Email already exists"}), 409
    try:
        new_user = User(username=username, email=email); new_user.set_password(password)
        db.session.add(new_user); db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e: db.session.rollback(); app.logger.error(f"DB error on register: {e}", exc_info=True); return jsonify({"message": "Server error"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    # ... (same implementation) ...
    data = request.get_json();
    if not data or not data.get('username') or not data.get('password'): return jsonify({"message": "Missing fields"}), 400
    username, password = data['username'], data['password']
    try:
        user = db.session.scalar(db.select(User).filter_by(username=username))
        if not user or not user.check_password(password): return jsonify({"message": "Invalid credentials"}), 401
        if update_train_yaml(user.username): # Call the function with the authenticated user's username
            app.logger.info(f"train.yaml update successful for user '{user.username}' upon login.")
        else:
            # Log the error, but still allow login.
            # The update_train_yaml function itself logs detailed errors.
            app.logger.warning(f"train.yaml update failed for user '{user.username}' upon login. Check previous logs. Login will proceed.")
        # --- End train.yaml update ---
        access_token = create_access_token(identity=user.username)
        return jsonify({"message": "Login successful", "access_token": access_token, "user": {"username": user.username, "email": user.email}}), 200
    except Exception as e: app.logger.error(f"Error during login: {e}", exc_info=True); return jsonify({"message": "Server error"}), 500

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    # ... (same implementation) ...
    current_user_username = get_jwt_identity()
    user = db.session.scalar(db.select(User).filter_by(username=current_user_username))
    if not user: return jsonify({"message": "Authenticated user not found"}), 404
    return jsonify({ "message": f"Hello {user.username}!", "logged_in_as": user.username}), 200

# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error): return jsonify({"message": "The requested resource was not found."}), 404
@app.errorhandler(500)
def internal_error(error):
    # ... (same implementation) ...
    app.logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    try: db.session.rollback()
    except Exception: pass
    return jsonify({"message": "An internal server error occurred."}), 500
# --- Template for train.yaml ---



# --- Add this helper function to update convert.yaml
def update_convert_yaml(username):
    """
    Updates the convert.yaml file to use the current user\\'s dataset paths
    """
    app.logger.info(f"[update_convert_yaml] Called for user: {username}")

    # SHARED_INFER_YAML_PATH is defined globally as '/specs/infer.yaml'
    # convert.yaml is in the same directory.
    # Use the directory of SHARED_INFER_YAML_PATH to construct the path to convert.yaml
    base_specs_path_in_container = os.path.dirname(SHARED_INFER_YAML_PATH) # Should be '/specs'
    absolute_convert_yaml_path = os.path.join(base_specs_path_in_container, 'convert.yaml') # Should be '/specs/convert.yaml'
    
    app.logger.info(f"[update_convert_yaml] SHARED_INFER_YAML_PATH is '{SHARED_INFER_YAML_PATH}'")
    app.logger.info(f"[update_convert_yaml] Target convert.yaml path (derived from SHARED_INFER_YAML_PATH's directory) set to: '{absolute_convert_yaml_path}'")

    try:
        # The directory os.path.dirname(SHARED_INFER_YAML_PATH) (i.e., /specs)
        # is already ensured to exist by os.makedirs in the app's boilerplate setup.
        # So, we primarily need to check if convert.yaml itself exists, though 'w' mode will create it.
        if not os.path.exists(absolute_convert_yaml_path):
            app.logger.warning(f"[update_convert_yaml] convert.yaml not found at the target path: '{absolute_convert_yaml_path}'. It will be created by the write operation.")
        
        # Create the odvg directory if it doesn\\'t exist (host path via app.config['UPLOAD_FOLDER'])
        # This path is where the application writes, so it uses app.config['UPLOAD_FOLDER'] which should map to /app/uploads
        host_odvg_annotations_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'finetune_datasets', username, 'odvg', 'annotations')
        app.logger.info(f"[update_convert_yaml] Ensuring ODVG annotations directory exists at host-mapped path: {host_odvg_annotations_dir}")
        try:
            os.makedirs(host_odvg_annotations_dir, exist_ok=True)
            app.logger.info(f"[update_convert_yaml] Successfully ensured ODVG annotations directory exists at: {host_odvg_annotations_dir}")
        except PermissionError as pe:
            app.logger.error(f"[update_convert_yaml] Permission error creating ODVG directory {host_odvg_annotations_dir}: {pe}", exc_info=True)
            return False
        except Exception as e_mkdir_odvg:
            app.logger.error(f"[update_convert_yaml] Error creating ODVG directory {host_odvg_annotations_dir}: {e_mkdir_odvg}", exc_info=True)
            return False

        # Define paths for YAML content (these are paths *inside* the inference container's perspective, starting with /data)
        container_data_base_path = '/data/finetune_datasets' # '/data' in container maps to 'uploads' on host (e.g., /app/uploads)
        container_user_odvg_annotations_path = f"{container_data_base_path}/{username}/odvg/annotations/"
        container_user_coco_train_json_path = f"{container_data_base_path}/{username}/coco/annotations/train.json"
        
        app.logger.info(f"[update_convert_yaml] YAML 'results_dir' will be: {container_user_odvg_annotations_path}")
        app.logger.info(f"[update_convert_yaml] YAML 'coco.ann_file' will be: {container_user_coco_train_json_path}")

        yaml_content = {
            'data': {
                'input_format': 'COCO',
                'output_format': 'ODVG'
            },
            'results_dir': container_user_odvg_annotations_path,
            'coco': {
                'ann_file': container_user_coco_train_json_path
            }
        }

        # Write to the file using the corrected absolute_convert_yaml_path
        app.logger.info(f"[update_convert_yaml] Attempting to write to convert.yaml at: '{absolute_convert_yaml_path}'")
        with open(absolute_convert_yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
            
        app.logger.info(f"[update_convert_yaml] Successfully updated convert.yaml for user {username} at '{absolute_convert_yaml_path}'")
        return True
        
    except FileNotFoundError: # Should be rare if /specs exists and permissions are okay
        app.logger.error(f"[update_convert_yaml] FileNotFoundError when trying to open/write convert.yaml at '{absolute_convert_yaml_path}'. This implies '/specs' might be missing or not accessible.", exc_info=True)
        return False
    except PermissionError as pe:
        app.logger.error(f"[update_convert_yaml] PermissionError when trying to write to convert.yaml at '{absolute_convert_yaml_path}': {pe}", exc_info=True)
        return False
    except Exception as e:
        app.logger.error(f"[update_convert_yaml] Generic error updating convert.yaml for user {username} at path '{absolute_convert_yaml_path}': {str(e)}", exc_info=True)
        return False

# --- Main Execution Block ---
if __name__ == '__main__':
    # ... (same implementation) ...
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    use_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host=host, port=port, debug=use_debug)