# Authentication Workflow

## Overview
Complete authentication system integration between frontend and backend with JWT tokens.

## Backend Configuration
- Custom User model with email as USERNAME_FIELD
- JWT authentication endpoints at `/api/token/` and `/api/token/refresh/`
- Professional error handling for authentication failures

## Frontend Implementation
- Central API service with automatic token management
- React Context for authentication state
- Protected routes with automatic redirects
- Professional error messages and success notifications

## Features
- Email-based authentication
- Automatic token refresh
- Field-specific error messages
- Success notifications with personalized welcome
- Persistent sessions across page refreshes

## Usage
1. User enters email/password on login page
2. Frontend sends credentials to `/api/token/`
3. Backend validates and returns JWT tokens
4. Frontend stores tokens and fetches user profile
5. User is redirected to dashboard with welcome notification

## Error Handling
- "Invalid credentials" - both email and password wrong
- "Incorrect password" - password wrong
- "Incorrect email address" - email not found
- Network error handling with user-friendly messages