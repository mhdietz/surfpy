import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from datetime import datetime, time, date

# Database connection string
# db_url = "postgresql://postgres:kooksinthekitchen@db.ehrfwjekssrnbgmgxctg.supabase.co:5432/postgres"
db_url = "postgresql://postgres.ehrfwjekssrnbgmgxctg:kooksinthekitchen@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_all_sessions():
    """Retrieve all surf sessions with user display name information"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all session data plus the user display name from metadata
            cur.execute("""
                SELECT s.*, 
                       u.email as user_email,
                       COALESCE(
                           u.raw_user_meta_data->>'display_name',
                           NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                           split_part(u.email, '@', 1)
                       ) as display_name
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
            sessions = cur.fetchall()
            # Convert to a list so we can modify it
            sessions_list = list(sessions)
            
            # Process each session to handle non-serializable types (like time objects)
            for i, session in enumerate(sessions_list):
                # Process time objects
                if 'time' in session and isinstance(session['time'], time):
                    sessions_list[i]['time'] = session['time'].isoformat()
                
                # Process date objects
                if 'date' in session and isinstance(session['date'], date):
                    sessions_list[i]['date'] = session['date'].isoformat()
            
            return sessions_list
    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()


def get_session(session_id):
    """Retrieve a single surf session including user display name"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.*, 
                       u.email as user_email,
                       COALESCE(
                           u.raw_user_meta_data->>'display_name',
                           NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                           split_part(u.email, '@', 1)
                       ) as display_name
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.id = %s
            """, (session_id,))
            session = cur.fetchone()
            if session:
                # Convert time objects to strings
                if 'time' in session and isinstance(session['time'], time):
                    session['time'] = session['time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in session and isinstance(session['date'], date):
                    session['date'] = session['date'].isoformat()
                    
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

            # Remove created_at if present
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
            
            # 1. CURRENT USER STATS
            cur.execute("""
                SELECT 
                    -- All-time stats
                    COUNT(*) as total_sessions_all_time,
                    
                    -- This year stats
                    COUNT(CASE WHEN EXTRACT(YEAR FROM date) = %s THEN 1 END) as total_sessions_this_year,
                    
                    -- Sessions per week this year (approximate)
                    ROUND(
                        (COUNT(CASE WHEN EXTRACT(YEAR FROM date) = %s THEN 1 END)::numeric / 
                        GREATEST(EXTRACT(WEEK FROM CURRENT_DATE), 1))::numeric, 2
                    ) as sessions_per_week_this_year,
                    
                    -- Average fun rating this year
                    ROUND(
                        AVG(CASE WHEN EXTRACT(YEAR FROM date) = %s THEN CAST(fun_rating AS FLOAT) END)::numeric, 2
                    ) as avg_fun_rating_this_year
                    
                FROM surf_sessions_duplicate 
                WHERE user_id = %s
            """, (current_year, current_year, current_year, current_user_id))
            
            current_user_stats = cur.fetchone()
            
            # 2. OTHER USERS STATS
            cur.execute("""
                SELECT 
                    s.user_id,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    
                    -- All-time stats
                    COUNT(*) as total_sessions_all_time,
                    
                    -- This year stats
                    COUNT(CASE WHEN EXTRACT(YEAR FROM s.date) = %s THEN 1 END) as total_sessions_this_year,
                    
                    -- Sessions per week this year
                    ROUND(
                        (COUNT(CASE WHEN EXTRACT(YEAR FROM s.date) = %s THEN 1 END)::numeric / 
                        GREATEST(EXTRACT(WEEK FROM CURRENT_DATE), 1))::numeric, 2
                    ) as sessions_per_week_this_year,
                    
                    -- Average fun rating this year
                    ROUND(
                        AVG(CASE WHEN EXTRACT(YEAR FROM s.date) = %s THEN CAST(s.fun_rating AS FLOAT) END)::numeric, 2
                    ) as avg_fun_rating_this_year
                    
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.user_id != %s  -- Exclude current user
                GROUP BY s.user_id, u.raw_user_meta_data, u.email
                ORDER BY total_sessions_all_time DESC
            """, (current_year, current_year, current_year, current_user_id))
            
            other_users_stats = cur.fetchall()
            
            # 3. COMMUNITY STATS (ALL USERS COMBINED)
            cur.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    ROUND(SUM(CAST(fun_rating AS FLOAT))::numeric, 1) as total_stoke
                FROM surf_sessions_duplicate
            """)
            
            community_stats = cur.fetchone()
            
            # Convert results to dictionaries and handle None values
            current_user_data = dict(current_user_stats) if current_user_stats else {
                'total_sessions_all_time': 0,
                'total_sessions_this_year': 0,
                'sessions_per_week_this_year': 0,
                'avg_fun_rating_this_year': None
            }
            
            other_users_data = [dict(user) for user in other_users_stats] if other_users_stats else []
            
            community_data = dict(community_stats) if community_stats else {
                'total_sessions': 0,
                'total_stoke': 0
            }
            
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
