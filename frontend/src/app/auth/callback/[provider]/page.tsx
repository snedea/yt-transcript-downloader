"use client"

import { useEffect, useRef } from 'react'
import { useRouter, useParams, useSearchParams } from 'next/navigation'
import { api } from '@/services/api'
import { useAuth } from '@/context/AuthContext'

export default function OAuthCallbackPage({ params }: { params: { provider: string } }) {
    const router = useRouter()
    const searchParams = useSearchParams()
    const { login } = useAuth()
    const processed = useRef(false)
    const { provider } = params

    useEffect(() => {
        const handleCallback = async () => {
            // Prevent double firing in strict mode
            if (processed.current) return
            processed.current = true

            // Get 'code' or 'error' from searchParams
            const code = searchParams.get('code')
            const error = searchParams.get('error')

            if (error) {
                console.error("OAuth error", error)
                router.push(`/login?error=${error}`)
                return
            }

            if (!code) {
                console.error("No code provided")
                router.push('/login?error=no_code')
                return
            }

            try {
                // Exchange code for tokens
                const response = await api.get(`/api/auth/oauth/callback/${provider}?code=${code}`)
                const { access_token, refresh_token } = response.data
                login(access_token, refresh_token)
            } catch (err: any) {
                console.error("OAuth exchange failed", err)
                router.push('/login?error=oauth_failed')
            }
        }

        handleCallback()
    }, [provider, searchParams, login, router])

    return (
        <div className="flex min-h-screen items-center justify-center">
            <div className="text-center">
                <h2 className="text-xl font-semibold mb-2">Authenticating...</h2>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            </div>
        </div>
    )
}
