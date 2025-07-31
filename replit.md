# Entrelíneas

## Overview

Entrelíneas is a Flask-based web application that transforms user emotions into elegant poetic phrases using OpenAI's GPT-4o model. The application allows users to input their emotional state and select from different poetic styles to generate personalized, poetic expressions in Spanish. Users can save their favorite phrases and maintain a collection of all generated content. By J.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via DATABASE_URL environment variable
- **AI Integration**: OpenAI GPT-4o API for phrase generation
- **Session Management**: Flask sessions with ProxyFix middleware for deployment

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **Styling**: Custom CSS with CSS variables for consistent theming
- **JavaScript**: Vanilla JavaScript for interactive features (character counting, form validation, loading states)
- **Fonts**: Google Fonts (Crimson Text for headings, Source Sans Pro for body text)

### Database Schema
Single table design with the `Phrase` model containing:
- Primary key (`id`)
- Original emotion text (`original_emotion`)
- Style selection (`style`)
- Generated phrase (`generated_phrase`)
- Creation timestamp (`created_at`)
- Favorite status (`is_favorite`)

## Key Components

### Core Services
1. **OpenAI Service** (`openai_service.py`): Handles AI phrase generation with style-specific prompts
2. **Models** (`models.py`): SQLAlchemy database models with JSON serialization
3. **Routes** (`routes.py`): Flask route handlers for web requests
4. **Templates**: HTML templates for user interface rendering

### Style Options
- **Poética minimalista**: Minimalist and elegant poetry
- **Indirecta redes**: Subtle phrases perfect for social media
- **Diario íntimo**: Intimate and personal diary-style expressions
- **Reflexiva**: Deep and thoughtful reflections

### User Interface Features
- Emotion input with character limit (500 characters)
- Style selection dropdown
- Generated phrase display
- Favorite toggling functionality
- Collection and favorites viewing
- Responsive design for mobile and desktop

## Data Flow

1. User inputs emotion and selects style on main page
2. Form submission triggers OpenAI API call with style-specific prompt
3. Generated phrase is saved to database with metadata
4. User is redirected to result page showing the generated phrase
5. User can mark phrases as favorites or view their collection
6. All interactions are logged and stored for future reference

## External Dependencies

### Required APIs
- **OpenAI API**: GPT-4o model for phrase generation (requires OPENAI_API_KEY)

### Python Packages
- Flask and Flask-SQLAlchemy for web framework and ORM
- OpenAI Python client for API integration
- Werkzeug for WSGI middleware

### Frontend Dependencies
- Bootstrap 5 via CDN for responsive UI components
- Font Awesome for icons
- Google Fonts for typography

## Deployment Strategy

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `OPENAI_API_KEY`: OpenAI API authentication key

### Application Structure
- Entry point: `main.py` imports and runs the Flask app
- Configuration: Environment-based with sensible defaults
- Database: Automatic table creation on startup
- Error Handling: Debug logging and user-friendly error messages

### Production Considerations
- ProxyFix middleware configured for reverse proxy deployment
- Database connection pooling with health checks
- Configurable host and port settings
- Debug mode controllable via environment

The application is designed to be easily deployable on platforms like Replit, Heroku, or similar cloud services with minimal configuration requirements.