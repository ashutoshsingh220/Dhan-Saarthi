import { createContext, useContext, useEffect, useState } from "react";
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
import { api } from "@/services/api";
import { AuthResult, ProfileResponse, Twin, User } from "@/types/api";

type AuthState = {
  token: string | null;
  user: User | null;
  profile: ProfileResponse | null;
  twin: Twin | null;
  onboardingComplete: boolean;
  loading: boolean;
  authenticate: (result: AuthResult) => Promise<void>;
  signOut: () => Promise<void>;
  setTwin: (twin: Twin) => void;
  setProfile: (profile: ProfileResponse) => void;
  refreshState: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);
const tokenKey = "dhan_saarthi_access_token";

async function getStoredToken(): Promise<string | null> {
  if (Platform.OS === "web") {
    try {
      return typeof window !== "undefined" ? localStorage.getItem(tokenKey) : null;
    } catch {
      return null;
    }
  }
  try {
    return await SecureStore.getItemAsync(tokenKey);
  } catch {
    return null;
  }
}

async function saveStoredToken(token: string): Promise<void> {
  if (Platform.OS === "web") {
    try {
      if (typeof window !== "undefined") localStorage.setItem(tokenKey, token);
    } catch {}
    return;
  }
  try {
    await SecureStore.setItemAsync(tokenKey, token);
  } catch {}
}

async function removeStoredToken(): Promise<void> {
  if (Platform.OS === "web") {
    try {
      if (typeof window !== "undefined") localStorage.removeItem(tokenKey);
    } catch {}
    return;
  }
  try {
    await SecureStore.deleteItemAsync(tokenKey);
  } catch {}
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [twin, setTwin] = useState<Twin | null>(null);
  const [onboardingComplete, setComplete] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadUserData = async (authToken: string) => {
    try {
      const meResult = await api.me(authToken);
      setUser(meResult.user);
      setComplete(meResult.onboarding_complete);
      setToken(authToken);

      if (meResult.onboarding_complete) {
        try {
          const prof = await api.getProfile(authToken);
          setProfile(prof);
        } catch {
          // Profile optional fallback
        }
        try {
          const t = await api.getTwin(authToken);
          setTwin(t);
        } catch {
          setTwin(null);
        }
      }
    } catch {
      await removeStoredToken();
      setToken(null);
      setUser(null);
      setProfile(null);
      setTwin(null);
      setComplete(false);
    }
  };

  useEffect(() => {
    (async () => {
      const saved = await getStoredToken();
      if (saved) {
        await loadUserData(saved);
      }
      setLoading(false);
    })();
  }, []);

  const refreshState = async () => {
    if (token) {
      setLoading(true);
      await loadUserData(token);
      setLoading(false);
    }
  };

  const authenticate = async (result: AuthResult) => {
    await saveStoredToken(result.access_token);
    setToken(result.access_token);
    setUser(result.user);
    setComplete(result.onboarding_complete);
    if (result.onboarding_complete) {
      await loadUserData(result.access_token);
    }
  };

  const signOut = async () => {
    await removeStoredToken();
    setToken(null);
    setUser(null);
    setProfile(null);
    setTwin(null);
    setComplete(false);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        profile,
        twin,
        onboardingComplete,
        loading,
        authenticate,
        signOut,
        setTwin,
        setProfile,
        refreshState,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const value = useContext(AuthContext);
  if (!value) throw new Error("AuthProvider is required");
  return value;
};
