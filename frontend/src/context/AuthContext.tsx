"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/services/api' // We will update api to handle auth header

interface User {
    id: string
    email: string
    username?: string
    full_name?: string
    avatar_url?: string
    is_active: boolean
    is_verified: boolean
}

interface AuthContextType {
    user: User | null
    isLoading: boolean
    isAuthenticated: boolean
    login: (token: string, refreshToken: string) => void
    logout: () => void
    refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const router = useRouter()

    // Initialize auth state
    useEffect(() => {
        const initAuth = async () => {
            const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
            if (token) {
                try {
                    // Fetch user profile
                    const response = await api.get<User>('/api/auth/me')
                    setUser(response.data)
                } catch (error) {
                    console.error("Failed to fetch user profile", error)
                    // If 401, token might be expired. 
                    // The api interceptor (to be implemented) should handle refresh.
                    // If refresh fails, it will likely throw here or we catch it.
                    // For now, if fetch fails, logging out might be safer unless it's network error.
                    // But lets wait for api interceptor logic.
                    // If we assume api interceptor handles refresh loop transparently, 
                    // then error here means refresh failed or network error.
                    // localStorage.removeItem('access_token')
                    // localStorage.removeItem('refresh_token')
                }
            }
            setIsLoading(false)
        }

        initAuth()
    }, [])

    const login = (token: string, refreshToken: string) => {
        localStorage.setItem('access_token', token)
        localStorage.setItem('refresh_token', refreshToken)
        // Immediately fetch user
        api.get<User>('/api/auth/me').then(res => {
            setUser(res.data)
            router.push('/') // Redirect to home page after login
        }).catch(err => {
            console.error("Login fetch user failed", err)
            // Still set user based on decoded token? No, safer to wait.
        })
    }

    const logout = async () => {
        try {
            // Get refresh token before removing from localStorage
            const refreshToken = localStorage.getItem('refresh_token')

            if (refreshToken) {
                // Call backend to revoke refresh token
                // This prevents the token from being used to generate new access tokens
                await api.post('/api/auth/logout', { refresh_token: refreshToken })
            }
        } catch (error) {
            // If logout fails on backend, still proceed with local logout
            console.error('Server logout failed:', error)
        } finally {
            // Always clear local storage and state
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            setUser(null)
            router.push('/login')
        }
    }

    const refreshUser = async () => {
        try {
            const response = await api.get<User>('/api/auth/me')
            setUser(response.data)
        } catch (error) {
            console.error("Refresh user failed", error)
        }
    }

    return (
        <AuthContext.Provider value={{
            user,
            isLoading,
            isAuthenticated: !!user,
            login,
            logout,
            refreshUser
        }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
