import { createContext, useContext, useState, useEffect} from 'react';
import type { ReactNode } from "react";

import { authAPI, setToken, clearToken, getToken } from './api-client';
import type { UserProfileResponse } from './api-types';

interface AuthContextType {
  user: UserProfileResponse | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      const userData = await authAPI.me(token);
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authAPI.login({ username: email, password });
    console.log("Login response:", response);
    setToken(response.access_token);
    await fetchUser();
  };

  const register = async (name: string, email: string, password: string) => {
    const response = await authAPI.register({ email, password, name });
    setToken(response.access_token);
    await fetchUser();
  };

  const logout = () => {
    clearToken();
    setUser(null);
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
