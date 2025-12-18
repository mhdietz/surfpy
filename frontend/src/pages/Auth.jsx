import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/UI/Button';
import Input from '../components/UI/Input';
import Card from '../components/UI/Card';
import Logo from '../components/UI/Logo';
import toast from 'react-hot-toast';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isLogin) {
        await login(email, password);
        toast.success('Logged in successfully!');
      } else {
        await signup(email, password, firstName, lastName);
        toast.success('Account created successfully!');
      }
      navigate('/feed'); // Redirect to feed on success
    } catch (err) {
      toast.error(err.message || 'An error occurred.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center items-center p-4">
      <div className="flex flex-col items-center mb-8"> 
        <Logo className="h-20 w-20 text-blue-600" />
        <h1 className="text-6xl font-bold text-gray-800 tracking-tight">slapp</h1> 
      </div>
      
      <Card>
        <div className="text-center">
          <h2 className="text-3xl font-bold">{isLogin ? 'Login' : 'Sign Up'}</h2>
        </div>
        <form className="space-y-6" onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div>
                <label htmlFor="firstName" className="text-sm font-medium text-gray-700">First Name</label>
                <Input
                  id="firstName"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label htmlFor="lastName" className="text-sm font-medium text-gray-700">Last Name</label>
                <Input
                  id="lastName"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </div>
            </>
          )}
          <div>
            <label htmlFor="email" className="text-sm font-medium text-gray-700">Email</label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <div className="flex justify-between items-center">
              <label htmlFor="password" className="text-sm font-medium text-gray-700">Password</label>
              {!isLogin && (
                <span className="text-xs text-gray-500">you only get one shot don't be a kook</span>
              )}
            </div>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <div>
            <Button type="submit" variant="primary">
              {isLogin ? 'Login' : 'Sign Up'}
            </Button>
          </div>
        </form>
        <div className="text-center">
          <button onClick={() => setIsLogin(!isLogin)} className="text-sm text-blue-600 hover:underline bg-transparent border-none">
            {isLogin ? 'Need an account? Sign Up' : 'Have an account? Login'}
          </button>
        </div>
      </Card>
      <div className="mt-4 text-center">
        <Link to="/about" className="text-sm text-blue-600 hover:underline">
          About
        </Link>
      </div>
    </div>
  );
};

export default AuthPage;
