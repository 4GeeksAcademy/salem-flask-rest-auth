import { useEffect, useState } from 'react';
import { loginUser } from '../data/starWarsData.jsx';
import useGlobalReducer from '../hooks/useGlobalReducer.jsx';

const Login = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [animationClass, setAnimationClass] = useState('');
  const { dispatch } = useGlobalReducer();

  useEffect(() => {
    // Play theme song on component load
    dispatch({
      type: "play_audio",
      payload: "https://ia600304.us.archive.org/30/items/StarWarsTheImperialMarchDarthVadersTheme/Star%20Wars-%20The%20Imperial%20March%20(Darth%20Vader's%20Theme).mp3"
    });
  }, [dispatch]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await loginUser(email, password);
      console.log('Login success:', response);
      
      // Trigger exit animation before login success
      setAnimationClass('login-credits-exit-ultra-slow');
      
      // Wait for animation to complete before calling onLoginSuccess
      setTimeout(() => {
        onLoginSuccess(response.user);
      }, 12000); // 12 seconds to match ultra-slow animation duration
      
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100 position-relative">
      <div className={`bg-black rounded-3 p-4 w-100 border border-light position-relative ${animationClass}`}
           style={{ 
             maxWidth: '400px',
             zIndex: 3,
             backgroundColor: 'rgba(0, 0, 0, 0.85)',
             backdropFilter: 'blur(5px)',
             boxShadow: '0 0 30px rgba(255, 255, 255, 0.1)'
           }}>
        <h2 className="text-center text-white mb-4">
          Login to Star Wars Blog
        </h2>
        
        {error && (
          <div className="alert alert-danger bg-danger  border-danger  text-danger text-center mb-3">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label text-white">
              Email:
            </label>
            <input
              type="email"
              className="form-control bg-black  border-light text-white"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="1@1.com"
            />
          </div>

          <div className="mb-4">
            <label className="form-label text-white">
              Password:
            </label>
            <input
              type="password"
              className="form-control bg-black  border-light text-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="123456"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100 mb-3"
          >
            Login
          </button>
          <p className="text-center text-white mb-4">
          To sign up, please contact the admin and pay a small fee of 1b.
          Test;
          user: 1@1.com
          pass: 1234567890
        </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
