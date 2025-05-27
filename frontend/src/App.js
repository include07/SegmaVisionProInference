// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import FinetunePage from './pages/FinetunePage'; // <-- Import FinetunePage
import ProtectedRoute from './components/ProtectedRoute';
import './App.css'; // Import CSS
import logo from './logo.png'; // <-- Import the logo
import agriVisionImg from './assets/agri-vision.png'; // Adjust filename/extension if needed
import industryVisionImg from './assets/industry-vision.jpg'; // Adjust filename/extension if needed
// Import the new form component
import ImageUploadForm from './components/ImageUploadForm';
// Simple Navbar component for navigation
function Navigation() {
  const { isLoggedIn, logout, currentUser } = useAuth();

  return (
    <nav className="app-nav"> {/* Add class for styling */}
      <Link to="/" className="nav-logo-link"> {/* Link for the logo */}
        <img src={logo} alt="App Logo" className="nav-logo" /> {/* Logo image */}
      </Link>
      <ul>
        {/* Keep Home link separate or integrate differently if needed */}
        {/* <li><Link to="/">Home</Link></li> */}
        {!isLoggedIn ? (
          <>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register">Register</Link></li>
          </>
        ) : (
          <>
             <li><Link to="/dashboard">Dashboard</Link></li>
             <li><Link to="/finetune">Finetune</Link></li> {/* Link to FinetunePage */}
             {/* User info and Logout pushed to the right by CSS */}
             <li className="nav-user-info">
                <span>{currentUser?.username}</span>
                <button onClick={logout} className="logout-button">Logout</button>
             </li>
          </>
        )}
      </ul>
    </nav>
  );
}

// UPDATED HomePage component
function HomePage() {
  const { isLoggedIn } = useAuth(); // <-- Get login status

  return (
    <div className="home-page-content">
      {/* Conditionally render Upload Form or Welcome Message */}
      {isLoggedIn ? (
        <ImageUploadForm /> // <-- Show upload form if logged in
      ) : (
        <>
          {/* Show SegmaVisionPro Intro if not logged in */}
          <header className="home-header">
            <h1>Welcome to SegmaVisionPro</h1>
            <p className="tagline">Revolutionizing Vision with Artificial Intelligence</p>
          </header>
          <section className="intro-text">
            <p>
              SegmaVisionPro delivers cutting-edge AI-powered visual analysis solutions tailored for the demands of modern agriculture, complex industrial processes, and beyond. Leverage the power of machine learning to unlock insights, automate tasks, and drive efficiency like never before.
            </p>
          </section>
           <div className="features-grid">
            {/* Agriculture Section */}
            <section className="feature-section">
                <div className="feature-image">
                <img src={agriVisionImg} alt="AI vision applied to agriculture" />
                </div>
                <div className="feature-text">
                <h2>Smart Agriculture</h2>
                <p>Optimize crop yields, monitor plant health in real-time, automate irrigation, and improve resource management with intelligent visual data analysis specific to agricultural needs.</p>
                </div>
            </section>
            {/* Industry Section */}
            <section className="feature-section feature-section-reverse">
                <div className="feature-image">
                <img src={industryVisionImg} alt="AI vision applied to industry" />
                </div>
                <div className="feature-text">
                <h2>Intelligent Industry</h2>
                <p>Enhance quality control, enable predictive maintenance, optimize production lines, and improve safety standards through advanced AI vision systems designed for industrial environments.</p>
                </div>
            </section>
            {/* Optional 'And More...' section */}
            </div>
            <footer className="home-footer">
                <p>Login or Register to upload images and access your dashboard.</p>
            </footer>
        </>
      )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        {/* Add class to the main container for global theme */}
        <div className="App futuristic-theme">
          <Navigation />
          <main className="main-content"> {/* Add class for styling */}
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route element={<ProtectedRoute />}>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/finetune" element={<FinetunePage />} /> {/* Protected route for FinetunePage */}
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;