import { createContext, useContext, useEffect, useState } from "react"
import type { ReactNode } from "react"

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const API_BASE = "/api/v1"
const TOKENS_KEY = "sports_analysis_tokens"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem(TOKENS_KEY)
    if (stored) {
      try {
        const tokens: AuthTokens = JSON.parse(stored)
        setAccessToken(tokens.access_token)
        setRefreshToken(tokens.refresh_token)
      } catch {
        localStorage.removeItem(TOKENS_KEY)
      }
    }
  }, [])

  const storeTokens = (tokens: AuthTokens) => {
    localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
    setAccessToken(tokens.access_token)
    setRefreshToken(tokens.refresh_token)
  }

  const login = async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || "Login failed")
    }
    const tokens: AuthTokens = await res.json()
    storeTokens(tokens)
  }

  const register = async (email: string, password: string, full_name: string) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || "Registration failed")
    }
    const tokens: AuthTokens = await res.json()
    storeTokens(tokens)
  }

  const logout = () => {
    localStorage.removeItem(TOKENS_KEY)
    setAccessToken(null)
    setRefreshToken(null)
  }

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        refreshToken,
        isAuthenticated: !!accessToken,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}

export function useApiClient() {
  const { accessToken } = useAuth()
  return {
    request: async (path: string, options: RequestInit = {}) => {
      const headers = new Headers(options.headers as Record<string, string>)
      if (accessToken) {
        headers.set("Authorization", `Bearer ${accessToken}`)
      }
      const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
      return res
    },
  }
}
