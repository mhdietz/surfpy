import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from datetime import datetime, time, date
import uuid
from psycopg2.extras import Json
from ocean_data.location import LEGACY_LOCATION_MAP

import os

# Database connection string
# Use environment variable for Vercel, with a fallback for local development
db_url = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:kooksinthekitchen@db.ehrfwjekssrnbgmgxctg.supabase.co:5432/postgres"
)

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_all_sessions(current_user_id):
    """Retrieve all surf sessions with user display name, participants, and shaka data"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all session data plus participants and shaka info
            cur.execute("""
                SELECT 
                    s.*, 
                    u.email as user_email,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'user_id', p_u.id,
                            'display_name', COALESCE(
                                p_u.raw_user_meta_data->>'display_name',
                                NULLIF(TRIM(COALESCE(p_u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(p_u.raw_user_meta_data->>'last_name', '')), ''),
                                split_part(p_u.email, '@', 1)
                            )
                        ))
                        FROM session_participants sp
                        JOIN auth.users p_u ON sp.user_id = p_u.id
                        WHERE sp.session_id = s.id
                    ), '[]'::jsonb) as participants,
                    jsonb_build_object(
                        'count', (SELECT COUNT(*) FROM session_shakas WHERE session_id = s.id),
                        'viewer_has_shakaed', EXISTS(SELECT 1 FROM session_shakas WHERE session_id = s.id AND user_id = %s),
                        'preview', COALESCE((
                            SELECT jsonb_agg(shaka_user.data)
                            FROM (
                                SELECT
                                    jsonb_build_object(
                                        'user_id', u_shaka.id,
                                        'display_name', COALESCE(
                                            u_shaka.raw_user_meta_data->>'display_name',
                                            NULLIF(TRIM(COALESCE(u_shaka.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u_shaka.raw_user_meta_data->>'last_name', '')), ''),
                                            split_part(u_shaka.email, '@', 1)
                                        )
                                    ) as data
                                FROM session_shakas ss
                                JOIN auth.users u_shaka ON ss.user_id = u_shaka.id
                                WHERE ss.session_id = s.id
                                ORDER BY ss.created_at DESC
                                LIMIT 2
                            ) as shaka_user
                        ), '[]'::jsonb)
                    ) as shakas
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """, (current_user_id,))
            sessions = cur.fetchall()
            # Convert to a list so we can modify it
            sessions_list = list(sessions)
            
            # Process each session to handle non-serializable types
            for i, session in enumerate(sessions_list):
                # Process time objects (start_time)
                if 'time' in session and isinstance(session['time'], time):
                    sessions_list[i]['time'] = session['time'].isoformat()
                
                # Process end_time objects
                if 'end_time' in session and isinstance(session['end_time'], time):
                    sessions_list[i]['end_time'] = session['end_time'].isoformat()
                
                # Process date objects
                if 'date' in session and isinstance(session['date'], date):
                    sessions_list[i]['date'] = session['date'].isoformat()
                
                # Convert participants from JSONB array to Python list
                if 'participants' in session and session['participants']:
                    # participants is already a list of dictionaries from the JSONB array
                    sessions_list[i]['participants'] = session['participants']
                else:
                    sessions_list[i]['participants'] = []
            
            return sessions_list
    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

# Add this new function to your database_utils.py file (place it near the other session functions)

def get_user_sessions(user_id):
    """Retrieve surf sessions for a specific user with participants and shaka data"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Same query structure as get_all_sessions but filtered by user_id
            cur.execute("""
                SELECT 
                    s.*, 
                    u.email as user_email,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'user_id', p_u.id,
                            'display_name', COALESCE(
                                p_u.raw_user_meta_data->>'display_name',
                                NULLIF(TRIM(COALESCE(p_u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(p_u.raw_user_meta_data->>'last_name', '')), ''),
                                split_part(p_u.email, '@', 1)
                            )
                        ))
                        FROM session_participants sp
                        JOIN auth.users p_u ON sp.user_id = p_u.id
                        WHERE sp.session_id = s.id
                    ), '[]'::jsonb) as participants,
                    jsonb_build_object(
                        'count', (SELECT COUNT(*) FROM session_shakas WHERE session_id = s.id),
                        'viewer_has_shakaed', EXISTS(SELECT 1 FROM session_shakas WHERE session_id = s.id AND user_id = %s),
                        'preview', COALESCE((
                            SELECT jsonb_agg(shaka_user.data)
                            FROM (
                                SELECT
                                    jsonb_build_object(
                                        'user_id', u_shaka.id,
                                        'display_name', COALESCE(
                                            u_shaka.raw_user_meta_data->>'display_name',
                                            NULLIF(TRIM(COALESCE(u_shaka.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u_shaka.raw_user_meta_data->>'last_name', '')), ''),
                                            split_part(u_shaka.email, '@', 1)
                                        )
                                    ) as data
                                FROM session_shakas ss
                                JOIN auth.users u_shaka ON ss.user_id = u_shaka.id
                                WHERE ss.session_id = s.id
                                ORDER BY ss.created_at DESC
                                LIMIT 2
                            ) as shaka_user
                        ), '[]'::jsonb)
                    ) as shakas
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.user_id = %s
                ORDER BY s.created_at DESC
            """, (user_id, user_id))
            
            sessions = cur.fetchall()
            # Convert to a list so we can modify it
            sessions_list = list(sessions)
            
            # Process each session to handle non-serializable types (same as get_all_sessions)
            for i, session in enumerate(sessions_list):
                # Process time objects (start_time)
                if 'time' in session and isinstance(session['time'], time):
                    sessions_list[i]['time'] = session['time'].isoformat()
                
                # Process end_time objects
                if 'end_time' in session and isinstance(session['end_time'], time):
                    sessions_list[i]['end_time'] = session['end_time'].isoformat()
                
                # Process date objects
                if 'date' in session and isinstance(session['date'], date):
                    sessions_list[i]['date'] = session['date'].isoformat()
                
                # Convert participants from JSONB array to Python list
                if 'participants' in session and session['participants']:
                    # participants is already a list of dictionaries from the JSONB array
                    sessions_list[i]['participants'] = session['participants']
                else:
                    sessions_list[i]['participants'] = []
            
            return sessions_list
    except Exception as e:
        print(f"Error retrieving user sessions: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def get_session(session_id, current_user_id):
    """Retrieve a single surf session including user display name, participants, and shaka data"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get session details plus participants and shaka info
            cur.execute("""
                SELECT 
                    s.*, 
                    u.email as user_email,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'user_id', p_u.id,
                            'display_name', COALESCE(
                                p_u.raw_user_meta_data->>'display_name',
                                NULLIF(TRIM(COALESCE(p_u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(p_u.raw_user_meta_data->>'last_name', '')), ''),
                                split_part(p_u.email, '@', 1)
                            )
                        ))
                        FROM session_participants sp
                        JOIN auth.users p_u ON sp.user_id = p_u.id
                        WHERE sp.session_id = s.id
                    ), '[]'::jsonb) as participants,
                    jsonb_build_object(
                        'count', (SELECT COUNT(*) FROM session_shakas WHERE session_id = s.id),
                        'viewer_has_shakaed', EXISTS(SELECT 1 FROM session_shakas WHERE session_id = s.id AND user_id = %s),
                        'preview', COALESCE((
                            SELECT jsonb_agg(shaka_user.data)
                            FROM (
                                SELECT
                                    jsonb_build_object(
                                        'user_id', u_shaka.id,
                                        'display_name', COALESCE(
                                            u_shaka.raw_user_meta_data->>'display_name',
                                            NULLIF(TRIM(COALESCE(u_shaka.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u_shaka.raw_user_meta_data->>'last_name', '')), ''),
                                            split_part(u_shaka.email, '@', 1)
                                        )
                                    ) as data
                                FROM session_shakas ss
                                JOIN auth.users u_shaka ON ss.user_id = u_shaka.id
                                WHERE ss.session_id = s.id
                                ORDER BY ss.created_at DESC
                                LIMIT 2
                            ) as shaka_user
                        ), '[]'::jsonb)
                    ) as shakas
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.id = %s
            """, (current_user_id, session_id))
            session = cur.fetchone()
            
            if session:
                # Convert time objects to strings
                if 'time' in session and isinstance(session['time'], time):
                    session['time'] = session['time'].isoformat()
                
                # Convert end_time objects to strings
                if 'end_time' in session and isinstance(session['end_time'], time):
                    session['end_time'] = session['end_time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in session and isinstance(session['date'], date):
                    session['date'] = session['date'].isoformat()
                
                # Convert participants from JSONB array to Python list
                if 'participants' in session and session['participants']:
                    # participants is already a list of dictionaries from the JSONB array
                    session['participants'] = session['participants']
                else:
                    session['participants'] = []
                    
            return session
    except Exception as e:
        print(f"Error retrieving session: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def create_session(session_data, user_id):
    """Create a new surf session in the database for a specific user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check the table structure to understand the ID column
            cur.execute("""
                SELECT column_name, column_default, is_identity 
                FROM information_schema.columns 
                WHERE table_name = 'surf_sessions_duplicate' AND column_name = 'id'
            """)
            id_info = cur.fetchone()
            
            # Find the maximum ID value currently in the table
            cur.execute("SELECT MAX(id) FROM surf_sessions_duplicate")
            max_id_result = cur.fetchone()
            max_id = max_id_result['max'] if max_id_result and 'max' in max_id_result else None
            
            # If max_id is None, start with 1, otherwise use max_id + 1
            next_id = 1 if max_id is None else max_id + 1
            print(f"Using next ID: {next_id}")
            
            # Always include the ID in the data to avoid conflicts
            session_data['id'] = next_id
            
            # Add user_id to the session data
            session_data['user_id'] = user_id
            
            # Handle raw_swell as JSONB
            if 'raw_swell' in session_data:
                session_data['raw_swell'] = Json(session_data['raw_swell'])

            # Handle raw_met as JSONB
            if 'raw_met' in session_data:
                session_data['raw_met'] = Json(session_data['raw_met'])
            
            # Handle raw_tide as JSONB
            if 'raw_tide' in session_data:
                session_data['raw_tide'] = Json(session_data['raw_tide'])

            # Handle session_tide_data as JSONB
            if 'session_tide_data' in session_data:
                session_data['session_tide_data'] = Json(session_data['session_tide_data'])

            # Remove created_at if present (it should be automatically generated by the DB)
            if 'created_at' in session_data:
                del session_data['created_at']
                
            columns = ', '.join(session_data.keys())
            placeholders = ', '.join(['%s'] * len(session_data))
            
            query = f"""
            INSERT INTO surf_sessions_duplicate ({columns}) 
            VALUES ({placeholders})
            RETURNING *
            """
            
            cur.execute(query, list(session_data.values()))
            conn.commit()
            
            # Handle serialization for time objects after fetching
            new_session = cur.fetchone()
            if new_session:
                # Convert time objects to strings
                if 'time' in new_session and isinstance(new_session['time'], time):
                    new_session['time'] = new_session['time'].isoformat()
                
                # Convert end_time objects to strings
                if 'end_time' in new_session and isinstance(new_session['end_time'], time):
                    new_session['end_time'] = new_session['end_time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in new_session and isinstance(new_session['date'], date):
                    new_session['date'] = new_session['date'].isoformat()
                    
            return new_session
    except Exception as e:
        print(f"Error creating session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def update_session(session_id, update_data, user_id):
    """Update an existing surf session for a specific user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check if the session belongs to the user
            cur.execute("SELECT id FROM surf_sessions_duplicate WHERE id = %s AND user_id = %s", (session_id, user_id))
            if not cur.fetchone():
                # Session doesn't exist or doesn't belong to user
                return None
            
            # Ensure id, created_at, and user_id aren't in the update data
            if 'id' in update_data:
                del update_data['id']
            if 'created_at' in update_data:
                del update_data['created_at']
            if 'user_id' in update_data:
                del update_data['user_id']  # Prevent user_id from being changed
            
            # Handle raw_swell as JSONB
            if 'raw_swell' in update_data:
                update_data['raw_swell'] = Json(update_data['raw_swell'])
                
            # Handle raw_met as JSONB
            if 'raw_met' in update_data:
                update_data['raw_met'] = Json(update_data['raw_met'])
            
            # Handle raw_tide as JSONB
            if 'raw_tide' in update_data:
                update_data['raw_tide'] = Json(update_data['raw_tide'])

            # Handle session_tide_data as JSONB
            if 'session_tide_data' in update_data:
                update_data['session_tide_data'] = Json(update_data['session_tide_data'])

            # Build SET clause for the SQL query
            set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
            
            query = f"""
            UPDATE surf_sessions_duplicate 
            SET {set_clause} 
            WHERE id = %s AND user_id = %s
            RETURNING *
            """
            
            # Add the session_id and user_id as the last parameters
            values = list(update_data.values()) + [session_id, user_id]
            
            cur.execute(query, values)
            conn.commit()
            
            # Handle serialization for time objects after fetching
            updated_session = cur.fetchone()
            if updated_session:
                # Convert time objects to strings
                if 'time' in updated_session and isinstance(updated_session['time'], time):
                    updated_session['time'] = updated_session['time'].isoformat()
                
                # Convert end_time objects to strings
                if 'end_time' in updated_session and isinstance(updated_session['end_time'], time):
                    updated_session['end_time'] = updated_session['end_time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in updated_session and isinstance(updated_session['date'], date):
                    updated_session['date'] = updated_session['date'].isoformat()
                    
            return updated_session
    except Exception as e:
        print(f"Error updating session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def delete_session(session_id, user_id):
    """Delete a surf session by its ID for a specific user"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM surf_sessions_duplicate WHERE id = %s AND user_id = %s RETURNING id", 
                        (session_id, user_id))
            deleted = cur.fetchone()
            conn.commit()
            return deleted is not None
    except Exception as e:
        print(f"Error deleting session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def toggle_shaka(session_id, user_id):
    """Toggle a 'shaka' on a surf session for a user."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if the shaka already exists
            cur.execute(
                "SELECT * FROM session_shakas WHERE session_id = %s AND user_id = %s",
                (session_id, user_id)
            )
            exists = cur.fetchone()

            if exists:
                # If it exists, delete it
                cur.execute(
                    "DELETE FROM session_shakas WHERE session_id = %s AND user_id = %s",
                    (session_id, user_id)
                )
            else:
                # If it does not exist, insert it
                cur.execute(
                    "INSERT INTO session_shakas (session_id, user_id) VALUES (%s, %s)",
                    (session_id, user_id)
                )

            # Get the new total count of shakas for the session
            cur.execute(
                "SELECT COUNT(*) as shaka_count FROM session_shakas WHERE session_id = %s",
                (session_id,)
            )
            result = cur.fetchone()
            shaka_count = result['shaka_count'] if result else 0

            conn.commit()
            return {"shaka_count": shaka_count}

    except Exception as e:
        print(f"Error toggling shaka: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_user_by_email(email):
    """Get user details by email"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Query the auth.users table (Supabase's built-in users table)
            cur.execute("SELECT * FROM auth.users WHERE email = %s", (email,))
            user = cur.fetchone()
            return user
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        conn.close()

def verify_user_session(access_token):
    """Verify a user's JWT token and return user_id if valid"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Query Supabase's sessions table to verify the token
            cur.execute("""
                SELECT user_id FROM auth.sessions 
                WHERE token = %s AND expires_at > NOW()
            """, (access_token,))
            session = cur.fetchone()
            if session:
                return session['user_id']
            return None
    except Exception as e:
        print(f"Error verifying user session: {e}")
        return None
    finally:
        conn.close()

def get_dashboard_stats(current_user_id):
    """Get comprehensive dashboard statistics for current user, other users, and community"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get current year for filtering
            current_year = datetime.now().year
            start_year = 2023
            years = list(range(start_year, current_year + 1))

            def _get_yearly_stats_sql(year, prefix, is_current_year_calc):
                # Use 52.14 for past years for a more accurate average weeks in a year
                # For the current year, use current week number
                sessions_per_week_divisor = "GREATEST(EXTRACT(WEEK FROM CURRENT_DATE), 1)" if is_current_year_calc else "52.14"
                
                return f"""
                    COUNT(CASE WHEN EXTRACT(YEAR FROM date) = {year} THEN 1 END) as {prefix}_total_sessions,
                    ROUND(
                        (COUNT(CASE WHEN EXTRACT(YEAR FROM date) = {year} THEN 1 END)::numeric / 
                        {sessions_per_week_divisor})::numeric, 2
                    ) as {prefix}_sessions_per_week,
                    ROUND(
                        AVG(CASE WHEN EXTRACT(YEAR FROM date) = {year} THEN CAST(fun_rating AS FLOAT) END)::numeric, 2
                    ) as {prefix}_avg_fun_rating,
                    ROUND(
                        AVG(CASE 
                            WHEN EXTRACT(YEAR FROM date) = {year} AND end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END)::numeric, 1
                    ) as {prefix}_avg_session_duration_minutes,
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN EXTRACT(YEAR FROM date) = {year} AND end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END), 0)::numeric, 1
                    ) as {prefix}_total_surf_time_minutes
                """

            # Build dynamic SELECT clauses for current user and other users
            current_user_yearly_selects = []
            for year in years:
                is_current_year_calc = (year == current_year)
                current_user_yearly_selects.append(_get_yearly_stats_sql(year, f'year_{year}', is_current_year_calc))
            
            other_users_yearly_selects = []
            for year in years:
                is_current_year_calc = (year == current_year)
                # For other users, the date column is s.date
                other_users_yearly_selects.append(_get_yearly_stats_sql(year, f'year_{year}', is_current_year_calc).replace('date', 's.date'))

            # 1. CURRENT USER STATS
            cur.execute(f"""
                SELECT 
                    -- All-time stats
                    COUNT(*) as total_sessions_all_time,
                    {', '.join(current_user_yearly_selects)}
                FROM surf_sessions_duplicate 
                WHERE user_id = %s
            """, (current_user_id,))
            
            current_user_stats = cur.fetchone()
            
            # 1b. CURRENT USER TOP LOCATIONS (NEW)
            cur.execute("""
                SELECT location, COUNT(*) as session_count 
                FROM surf_sessions_duplicate 
                WHERE user_id = %s AND EXTRACT(YEAR FROM date) = %s
                GROUP BY location 
                ORDER BY session_count DESC 
                LIMIT 3
            """, (current_user_id, current_year))
            
            user_top_locations = cur.fetchall()
            
            # 2. OTHER USERS STATS
            cur.execute(f"""
                SELECT 
                    s.user_id,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    
                    -- All-time stats
                    COUNT(*) as total_sessions_all_time,
                    {', '.join(other_users_yearly_selects)}
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.user_id != %s  -- Exclude current user
                GROUP BY s.user_id, u.raw_user_meta_data, u.email
                ORDER BY total_sessions_all_time DESC
            """, (current_user_id,))
            
            other_users_stats = cur.fetchall()
            
            # 3. COMMUNITY STATS (Enhanced with time calculations)
            cur.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    ROUND(SUM(CAST(fun_rating AS FLOAT))::numeric, 1) as total_stoke,
                    
                    -- Community average session duration (sessions with end_time)
                    ROUND(
                        AVG(CASE 
                            WHEN end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END)::numeric, 1
                    ) as avg_session_duration_minutes,
                    
                    -- Total community surf time in minutes (sessions with end_time)
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END), 0)::numeric, 1
                    ) as total_surf_time_minutes
                    
                FROM surf_sessions_duplicate
                WHERE EXTRACT(YEAR FROM date) = %s
            """, (current_year,))
            
            community_stats = cur.fetchone()
            
            # 3b. COMMUNITY TOP LOCATION (NEW)
            cur.execute("""
                SELECT location, COUNT(*) as session_count
                FROM surf_sessions_duplicate 
                WHERE EXTRACT(YEAR FROM date) = %s
                GROUP BY location 
                ORDER BY session_count DESC 
                LIMIT 1
            """, (current_year,))
            
            community_top_location = cur.fetchone()
            
            # Convert results to dictionaries and handle None values
            current_user_data = {
                'total_sessions_all_time': current_user_stats['total_sessions_all_time'] if current_user_stats else 0,
                'yearly_stats': {}
            }
            for year in years:
                prefix = f'year_{year}'
                current_user_data['yearly_stats'][year] = {
                    'total_sessions': current_user_stats[f'{prefix}_total_sessions'] if current_user_stats else 0,
                    'sessions_per_week': current_user_stats[f'{prefix}_sessions_per_week'] if current_user_stats else 0,
                    'avg_fun_rating': current_user_stats[f'{prefix}_avg_fun_rating'] if current_user_stats else None,
                    'avg_session_duration_minutes': current_user_stats[f'{prefix}_avg_session_duration_minutes'] if current_user_stats else None,
                    'total_surf_time_minutes': current_user_stats[f'{prefix}_total_surf_time_minutes'] if current_user_stats else 0
                }
                
                # Fetch top 3 locations for the current user for this specific year
                cur.execute("""
                    SELECT location, COUNT(*) as session_count 
                    FROM surf_sessions_duplicate 
                    WHERE user_id = %s AND EXTRACT(YEAR FROM date) = %s
                    GROUP BY location 
                    ORDER BY session_count DESC 
                    LIMIT 3
                """, (current_user_id, year))
                
                top_locations_for_year = cur.fetchall()
                current_user_data['yearly_stats'][year]['top_locations'] = [dict(loc) for loc in top_locations_for_year] if top_locations_for_year else []
            
            other_users_data = []
            if other_users_stats:
                for user_stat in other_users_stats:
                    user_data = {
                        'user_id': user_stat['user_id'],
                        'display_name': user_stat['display_name'],
                        'total_sessions_all_time': user_stat['total_sessions_all_time'],
                        'yearly_stats': {}
                    }
                    for year in years:
                        prefix = f'year_{year}'
                        user_data['yearly_stats'][year] = {
                            'total_sessions': user_stat[f'{prefix}_total_sessions'],
                            'sessions_per_week': user_stat[f'{prefix}_sessions_per_week'],
                            'avg_fun_rating': user_stat[f'{prefix}_avg_fun_rating'],
                            'avg_session_duration_minutes': user_stat[f'{prefix}_avg_session_duration_minutes'],
                            'total_surf_time_minutes': user_stat[f'{prefix}_total_surf_time_minutes']
                        }
                    other_users_data.append(user_data)
            
            community_data = dict(community_stats) if community_stats else {
                'total_sessions': 0,
                'total_stoke': 0,
                'avg_session_duration_minutes': None,
                'total_surf_time_minutes': 0
            }
            
            # Add top location to community data
            community_data['top_location'] = dict(community_top_location) if community_top_location else None
            
            return {
                'current_user': current_user_data,
                'other_users': other_users_data,
                'community': community_data
            }
            
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def generate_session_group_id():
    """Generate a unique UUID for linking related sessions"""
    return str(uuid.uuid4())

def create_session_with_participants(session_data, creator_user_id, tagged_user_ids=None):
    """
    Create a session with optional tagged participants.
    This creates a single session and then adds participants to it.
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Create the single session for the creator
            # The session_group_id is no longer needed for new sessions
            if 'session_group_id' in session_data:
                del session_data['session_group_id']
            
            original_session = create_session(session_data, creator_user_id)
            if not original_session:
                return None
            
            new_session_id = original_session['id']
            participant_records = []
            
            # 2. Create participant record for the creator
            cur.execute("""
                INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (new_session_id, creator_user_id, creator_user_id, 'creator'))
            
            creator_participant = cur.fetchone()
            if creator_participant:
                participant_records.append(dict(creator_participant))
            
            # 3. Create participant records for tagged users
            if tagged_user_ids:
                for tagged_user_id in tagged_user_ids:
                    cur.execute("""
                        INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                    """, (new_session_id, tagged_user_id, creator_user_id, 'tagged_participant'))
                    
                    tagged_participant = cur.fetchone()
                    if tagged_participant:
                        participant_records.append(dict(tagged_participant))
            
            # Commit the entire transaction
            conn.commit()
            
            return {
                'session': original_session,
                'participants': participant_records
            }
            
    except Exception as e:
        print(f"Error creating session with participants: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_participant_record(session_id, user_id, tagged_by_user_id, role):
    """Create a record in session_participants table"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (session_id, user_id, tagged_by_user_id, role))
            
            participant = cur.fetchone()
            return participant
            
    except Exception as e:
        print(f"Error creating participant record: {e}")
        raise
    finally:
        conn.close()

def get_session_participants(session_id):
    """Get all participants for a session"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    sp.*,
                    u.email as user_email,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name
                FROM session_participants sp
                LEFT JOIN auth.users u ON sp.user_id = u.id
                WHERE sp.session_id = %s
                ORDER BY sp.role DESC, sp.created_at ASC
            """, (session_id,))
            
            participants = cur.fetchall()
            return list(participants) if participants else []
            
    except Exception as e:
        print(f"Error getting session participants: {e}")
        return []
    finally:
        conn.close()

def get_sessions_by_location(location_slug, current_user_id):
    """Retrieve all surf sessions for a specific location, including participants and shaka data."""
    # Get the configuration for the given location slug from the database
    spot_config = get_surf_spot_by_slug(location_slug)
    if not spot_config:
        return []

    # Collect all possible names for the location
    possible_names = {location_slug, spot_config['name']}
    for legacy_name, slug in LEGACY_LOCATION_MAP.items():
        if slug == location_slug:
            possible_names.add(legacy_name)

    # Handle special case for Lido Beach (if still needed, as it might be covered by legacy map or direct slug)
    if location_slug == 'lido-beach':
        possible_names.add('lido')
        possible_names.add('Lido')
        possible_names.add('Lido, Long Beach')

    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # The query is similar to get_all_sessions, but with a WHERE clause for the location
            query = """
                SELECT
                    s1.*,
                    u1.email as user_email,
                    COALESCE(
                        u1.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u1.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u1.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u1.email, '@', 1)
                    ) as display_name,
                    COALESCE(
                        ARRAY_AGG(
                            DISTINCT jsonb_build_object(
                                'user_id', s2.user_id,
                                'display_name', COALESCE(
                                    u2.raw_user_meta_data->>'display_name',
                                    NULLIF(TRIM(COALESCE(u2.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u2.raw_user_meta_data->>'last_name', '')), ''),
                                    split_part(u2.email, '@', 1)
                                )
                            )
                        ) FILTER (WHERE s2.user_id != s1.user_id AND s2.user_id IS NOT NULL),
                        ARRAY[]::jsonb[]
                    ) as participants,
                    jsonb_build_object(
                        'count', (SELECT COUNT(*) FROM session_shakas WHERE session_id = s1.id),
                        'viewer_has_shakaed', EXISTS(SELECT 1 FROM session_shakas WHERE session_id = s1.id AND user_id = %s),
                        'preview', COALESCE((
                            SELECT jsonb_agg(shaka_user.data)
                            FROM (
                                SELECT
                                    jsonb_build_object(
                                        'user_id', u_shaka.id,
                                        'display_name', COALESCE(
                                            u_shaka.raw_user_meta_data->>'display_name',
                                            NULLIF(TRIM(COALESCE(u_shaka.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u_shaka.raw_user_meta_data->>'last_name', '')), ''),
                                            split_part(u_shaka.email, '@', 1)
                                        )
                                    ) as data
                                FROM session_shakas ss
                                JOIN auth.users u_shaka ON ss.user_id = u_shaka.id
                                WHERE ss.session_id = s1.id
                                ORDER BY ss.created_at DESC
                                LIMIT 2
                            ) as shaka_user
                        ), '[]'::jsonb)
                    ) as shakas
                FROM surf_sessions_duplicate s1
                LEFT JOIN auth.users u1 ON s1.user_id = u1.id
                LEFT JOIN surf_sessions_duplicate s2 ON s1.session_group_id = s2.session_group_id AND s1.session_group_id IS NOT NULL
                LEFT JOIN auth.users u2 ON s2.user_id = u2.id
                WHERE s1.location IN %s
                GROUP BY s1.id, s1.created_at, s1.session_name, s1.location, s1.fun_rating, s1.time, s1.session_notes,
                         s1.raw_swell, s1.date, s1.swell_buoy_id, s1.raw_met, s1.met_buoy_id, s1.raw_tide,
                         s1.tide_station_id, s1.user_id, s1.end_time, s1.session_group_id, u1.email, u1.raw_user_meta_data
                ORDER BY s1.created_at DESC
            """

            cur.execute(query, (current_user_id, tuple(possible_names)))
            sessions = cur.fetchall()
            sessions_list = list(sessions)

            # Process each session to handle non-serializable types
            for i, session in enumerate(sessions_list):
                if 'time' in session and isinstance(session['time'], time):
                    sessions_list[i]['time'] = session['time'].isoformat()
                if 'end_time' in session and isinstance(session['end_time'], time):
                    sessions_list[i]['end_time'] = session['end_time'].isoformat()
                if 'date' in session and isinstance(session['date'], date):
                    sessions_list[i]['date'] = session['date'].isoformat()
                if 'participants' in session and session['participants']:
                    sessions_list[i]['participants'] = session['participants']
                else:
                    sessions_list[i]['participants'] = []
            
            return sessions_list
    except Exception as e:
        print(f"Error retrieving sessions by location: {e}")
        raise
    finally:
        conn.close()

def get_surf_spot_by_slug(slug):
    """Retrieve a single surf spot by its slug from the database."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    id, created_at, slug, name, swell_buoy_id, tide_station_id, 
                    wind_lat, wind_long, breaking_wave_depth, breaking_wave_angle, 
                    breaking_wave_slope, timezone, met_buoy_id
                FROM surf_spots
                WHERE slug ILIKE %s
            """, (slug,))
            spot = cur.fetchone()
            return spot
    except Exception as e:
        print(f"Error retrieving surf spot by slug: {e}")
        return None
    finally:
        conn.close()

def get_all_surf_spots():
    """Retrieve all surf spots from the database."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    id, created_at, slug, name, swell_buoy_id, tide_station_id, 
                    wind_lat, wind_long, breaking_wave_depth, breaking_wave_angle, 
                    breaking_wave_slope, timezone, region
                FROM surf_spots
                ORDER BY name
            """)
            spots = cur.fetchall()
            return list(spots)
    except Exception as e:
        print(f"Error retrieving all surf spots: {e}")
        return []
    finally:
        conn.close()

def get_surf_spots_by_slugs(slugs):
    """Retrieve multiple surf spots by their slugs from the database."""
    if not slugs:
        return []
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Using IN clause for multiple slugs
            query = """
                SELECT 
                    id, created_at, slug, name, swell_buoy_id, tide_station_id, 
                    wind_lat, wind_long, breaking_wave_depth, breaking_wave_angle, 
                    breaking_wave_slope, timezone
                FROM surf_spots
                WHERE slug IN %s
                ORDER BY name
            """
            cur.execute(query, (tuple(slugs),))
            spots = cur.fetchall()
            return list(spots)
    except Exception as e:
        print(f"Error retrieving surf spots by slugs: {e}")
        return []
    finally:
        conn.close()

def get_surf_spot_by_name(name):
    """Retrieve a single surf spot by its name from the database."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    id, created_at, slug, name, swell_buoy_id, tide_station_id, 
                    wind_lat, wind_long, breaking_wave_depth, breaking_wave_angle, 
                    breaking_wave_slope, timezone, met_buoy_id
                FROM surf_spots
                WHERE name ILIKE %s
            """, (name,))
            spot = cur.fetchone()
            return spot
    except Exception as e:
        print(f"Error retrieving surf spot by name: {e}")
        return None
    finally:
        conn.close()
