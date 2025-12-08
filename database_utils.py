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

def _format_session_response(session):
    """Take a session dictionary from the DB and format it for the API response."""
    if not session:
        return None

    # Standardize all timestamp fields to ISO 8601 format
    for field in ['created_at', 'session_started_at', 'session_ended_at', 'next_tide_event_at']:
        if field in session and isinstance(session.get(field), datetime):
            session[field] = session[field].isoformat()

    # Group tide data into a single object
    tide_data = {}
    if 'session_water_level' in session and session.get('session_water_level') is not None:
        tide_data['water_level'] = session.pop('session_water_level')
    if 'tide_direction' in session and session.get('tide_direction') is not None:
        tide_data['direction'] = session.pop('tide_direction')
    if 'next_tide_event_type' in session and session.get('next_tide_event_type') is not None:
        tide_data['next_event_type'] = session.pop('next_tide_event_type')
    if 'next_tide_event_at' in session and session.get('next_tide_event_at') is not None:
        tide_data['next_event_at'] = session.pop('next_tide_event_at')
    if 'next_tide_event_height' in session and session.get('next_tide_event_height') is not None:
        tide_data['next_event_height'] = session.pop('next_tide_event_height')
    
    if tide_data:
        session['tide'] = tide_data
    else:
        session.pop('tide', None)

    # Convert participants from JSONB array to Python list
    if 'participants' in session and session['participants']:
        session['participants'] = session['participants']
    else:
        session['participants'] = []
    
    return session

def get_all_sessions(current_user_id, filters={}):
    """Retrieve all surf sessions with user display name, participants, and shaka data"""
    return get_session_summary_list(current_user_id, filters=filters)

# This function is now modified to accept a profile_user_id and a viewer_user_id
def get_user_sessions(profile_user_id, viewer_user_id, filters={}):
    """Retrieve surf sessions created by a specific user, with shaka data relative to the viewer."""
    return get_session_summary_list(viewer_user_id, profile_user_id_filter=profile_user_id, filters=filters)

def get_session_detail(session_id, current_user_id):
    """Retrieve a single surf session including user display name, participants, and shaka data"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get session details plus participants and shaka info
            cur.execute("""
                SELECT 
                    s.id, s.created_at, s.session_name, s.location, s.fun_rating, s.session_notes,
                    s.raw_swell, s.swell_buoy_id, s.raw_met, s.met_buoy_id,
                    s.tide_station_id, s.user_id, s.session_group_id,
                    s.session_water_level, s.tide_direction, s.next_tide_event_type, s.next_tide_event_at, s.next_tide_event_height,
                    s.session_started_at, s.session_ended_at,
                    u.email as user_email,
                    sp.slug as location_slug,
                    sp.timezone as location_timezone,
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
                    ) as shakas,
                    (SELECT COUNT(*) FROM comments WHERE session_id = s.id) as comment_count
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                LEFT JOIN surf_spots sp ON s.location = sp.name
                WHERE s.id = %s
            """, (current_user_id, session_id))
            session = cur.fetchone()
            
            return _format_session_response(session)
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

            # FIX: Handle tide_station_id which is incorrectly typed as jsonb
            if 'tide_station_id' in session_data and session_data['tide_station_id'] is not None:
                # The value might be an integer or already a JSON object.
                # psycopg2's Json adapter can handle both.
                session_data['tide_station_id'] = Json(session_data['tide_station_id'])

            # Remove deprecated fields
            session_data.pop('date', None)
            session_data.pop('time', None)
            session_data.pop('end_time', None)

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
            
            new_session = cur.fetchone()
            return _format_session_response(new_session)
    except Exception as e:
        print(f"Error creating session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def update_session(session_id, update_data, user_id, tagged_user_ids=None):
    """Update an existing surf session and its participants for a specific user."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First, check if the session belongs to the user
            cur.execute("SELECT id FROM surf_sessions_duplicate WHERE id = %s AND user_id = %s", (session_id, user_id))
            if not cur.fetchone():
                return None  # Session doesn't exist or doesn't belong to the user

            # --- Update Basic Session Details ---
            # Prevent key fields from being updated directly
            update_data.pop('id', None)
            update_data.pop('created_at', None)
            update_data.pop('user_id', None)
            
            # Handle JSONB fields
            if 'raw_swell' in update_data:
                update_data['raw_swell'] = Json(update_data['raw_swell'])
            if 'raw_met' in update_data:
                update_data['raw_met'] = Json(update_data['raw_met'])

            # Remove deprecated fields if they exist
            update_data.pop('date', None)
            update_data.pop('time', None)
            update_data.pop('end_time', None)

            # Only perform the update if there's data to update
            if update_data:
                set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
                query = f"""
                UPDATE surf_sessions_duplicate 
                SET {set_clause} 
                WHERE id = %s AND user_id = %s
                """
                values = list(update_data.values()) + [session_id, user_id]
                cur.execute(query, values)

            # --- Synchronize Session Participants ---
            if tagged_user_ids is not None:
                # 1. Delete all existing 'tagged' participants for this session
                cur.execute(
                    "DELETE FROM session_participants WHERE session_id = %s AND role = 'tagged_participant'",
                    (session_id,)
                )
                
                # 2. Insert the new list of tagged participants
                if tagged_user_ids:
                    for tagged_user_id in tagged_user_ids:
                        cur.execute(
                            """
                            INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (session_id, tagged_user_id, user_id, 'tagged_participant')
                        )

            # Commit the entire transaction
            conn.commit()
            
            # Fetch the fully updated session to return it
            # We can't just use RETURNING anymore because we might have multiple queries
            cur.execute("SELECT * FROM surf_sessions_duplicate WHERE id = %s", (session_id,))
            updated_session = cur.fetchone()
            
            return _format_session_response(updated_session)
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

def get_session_shakas(session_id):
    """Get all users who have reacted with shakas for a specific session, ordered by most recent first."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    ss.user_id,
                    ss.created_at,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name
                FROM session_shakas ss
                JOIN auth.users u ON ss.user_id = u.id
                WHERE ss.session_id = %s
                ORDER BY ss.created_at DESC
            """, (session_id,))
            
            shakas = cur.fetchall()
            
            # Format timestamps for JSON serialization
            formatted_shakas = []
            for shaka in shakas:
                formatted_shaka = dict(shaka)
                if isinstance(formatted_shaka['created_at'], datetime):
                    formatted_shaka['created_at'] = formatted_shaka['created_at'].isoformat()
                formatted_shakas.append(formatted_shaka)
            
            return formatted_shakas
            
    except Exception as e:
        print(f"Error getting session shakas: {e}")
        return None
    finally:
        conn.close()

def create_comment(session_id, user_id, comment_text):
    """Create a new comment for a session."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO comments (session_id, user_id, comment_text)
                VALUES (%s, %s, %s)
                RETURNING id, session_id, user_id, comment_text, created_at;
            """, (session_id, user_id, comment_text))
            
            new_comment = cur.fetchone()
            if new_comment:
                new_comment['comment_id'] = new_comment.pop('id')
            
            # Now, fetch the display_name for the user who commented
            cur.execute("""
                SELECT 
                    COALESCE(
                        raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(raw_user_meta_data->>'last_name', '')), ''),
                        split_part(email, '@', 1)
                    ) as display_name
                FROM auth.users
                WHERE id = %s
            """, (user_id,))
            
            user_info = cur.fetchone()
            new_comment['display_name'] = user_info['display_name']
            
            # Format timestamp
            if isinstance(new_comment['created_at'], datetime):
                new_comment['created_at'] = new_comment['created_at'].isoformat()
                
            conn.commit()
            return new_comment
            
    except Exception as e:
        print(f"Error creating comment: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_notification(recipient_user_id, sender_user_id, session_id, notification_type):
    """
    Creates a new notification in the database.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO notifications (recipient_user_id, sender_user_id, session_id, type)
                VALUES (%s, %s, %s, %s)
                RETURNING id, recipient_user_id, sender_user_id, session_id, type, read, created_at
            """, (recipient_user_id, sender_user_id, session_id, notification_type))
            
            new_notification = cur.fetchone()
            conn.commit()
            return new_notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        conn.rollback()
        # Log the specific error for debugging
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def get_notifications(user_id):
    """
    Retrieves all notifications for a given user, including sender and session details.
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    n.id,
                    n.recipient_user_id,
                    n.sender_user_id,
                    COALESCE(
                        sender_u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(sender_u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(sender_u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(sender_u.email, '@', 1)
                    ) AS sender_display_name,
                    n.session_id,
                    s.session_name AS session_title,
                    s.location AS session_spot,
                    s.session_started_at AS session_date,
                    n.type,
                    n.read,
                    n.created_at
                FROM notifications n
                JOIN auth.users sender_u ON n.sender_user_id = sender_u.id
                JOIN surf_sessions_duplicate s ON n.session_id = s.id
                WHERE n.recipient_user_id = %s
                ORDER BY n.created_at DESC
            """, (user_id,))
            
            notifications = cur.fetchall()
            
            # Format timestamps for JSON serialization
            formatted_notifications = []
            for notification in notifications:
                formatted_notification = dict(notification)
                if isinstance(formatted_notification['created_at'], datetime):
                    formatted_notification['created_at'] = formatted_notification['created_at'].isoformat()
                if isinstance(formatted_notification['session_date'], datetime):
                    formatted_notification['session_date'] = formatted_notification['session_date'].isoformat()
                formatted_notifications.append(formatted_notification)
            
            return formatted_notifications
    except Exception as e:
        print(f"Error retrieving notifications: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        conn.close()

def get_unread_notifications_count(user_id):
    """
    Retrieves the count of unread notifications for a given user.
    """
    conn = get_db_connection()
    if not conn:
        return 0

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT COUNT(*) AS unread_count
                FROM notifications
                WHERE recipient_user_id = %s AND read = FALSE
            """, (user_id,))
            
            result = cur.fetchone()
            return result['unread_count'] if result else 0
    except Exception as e:
        print(f"Error retrieving unread notifications count: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        conn.close()

def mark_notification_read(notification_id, user_id):
    """
    Marks a specific notification as read.
    Includes a user_id check to ensure only the recipient can mark it as read.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE notifications
                SET read = TRUE
                WHERE id = %s AND recipient_user_id = %s
                RETURNING id
            """, (notification_id, user_id))
            
            updated = cur.fetchone()
            conn.commit()
            return updated is not None
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def copy_session_as_new_user(original_session_id, new_user_id, sender_user_id):
    """
    Copies an existing session and creates a new one for a different user.
    Participants from the original session are copied, but no notifications are sent to them.
    Notes and fun_rating are reset. A 'session_snake' notification is created for the new user.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        # Get the original session details
        original_session = get_session_detail(original_session_id, sender_user_id) # Use sender_user_id as current_user_id for detail retrieval
        if not original_session:
            return None

        # Prepare new session data
        new_session_data = {
            'session_name': original_session.get('session_name'),
            'location': original_session.get('location'),
            'session_started_at': original_session.get('session_started_at'),
            'session_ended_at': original_session.get('session_ended_at'),
            'raw_swell': original_session.get('raw_swell'),
            'swell_buoy_id': original_session.get('swell_buoy_id'),
            'raw_met': original_session.get('raw_met'),
            'met_buoy_id': original_session.get('met_buoy_id'),
            'tide_station_id': original_session.get('tide_station_id'),
            'session_water_level': original_session.get('tide', {}).get('water_level'),
            'tide_direction': original_session.get('tide', {}).get('direction'),
            'next_tide_event_type': original_session.get('tide', {}).get('next_event_type'),
            'next_tide_event_at': original_session.get('tide', {}).get('next_event_at'),
            'next_tide_event_height': original_session.get('tide', {}).get('next_event_height'),
            'session_notes': None,  # Reset notes
            'fun_rating': 5      # Reset fun rating to a default of 5
        }

        # Extract participants from the original session for copying
        original_participants = original_session.get('participants', [])
        # The list of users to be tagged in the new session includes everyone
        # from the original session (both creator and tagged users) EXCEPT for the
        # person who is snaking the session (the new creator).
        tagged_user_ids = [p['user_id'] for p in original_participants if p['user_id'] != new_user_id] 

        # Create the new session for the new user
        # Pass send_notifications=False to prevent notifying copied participants
        created_session_result = create_session_with_participants(
            session_data=new_session_data,
            creator_user_id=new_user_id,
            tagged_user_ids=tagged_user_ids,
            send_notifications=False  # Do NOT send notifications to copied participants
        )

        if not created_session_result:
            return None

        new_session = created_session_result['session']
        new_session_id = new_session['id']

        conn.commit() # Commit changes if successful

        return new_session
    except Exception as e:
        print(f"Error copying session: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def get_comments_for_session(session_id):
    """Retrieve all comments for a specific session."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    c.id as comment_id,
                    c.session_id,
                    c.user_id,
                    c.comment_text,
                    c.created_at,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name
                FROM comments c
                JOIN auth.users u ON c.user_id = u.id
                WHERE c.session_id = %s
                ORDER BY c.created_at ASC
            """, (session_id,))
            
            comments = cur.fetchall()
            
            # Format timestamps
            for comment in comments:
                if isinstance(comment['created_at'], datetime):
                    comment['created_at'] = comment['created_at'].isoformat()
            
            return comments

    except Exception as e:
        print(f"Error getting comments for session: {e}")
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

def get_user_profile_by_id(user_id):
    """Get user profile details by user ID, including display name."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    id, 
                    email,
                    raw_user_meta_data->>'first_name' as first_name,
                    COALESCE(
                        raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(raw_user_meta_data->>'last_name', '')), ''),
                        split_part(email, '@', 1)
                    ) as display_name
                FROM auth.users 
                WHERE id = %s
            """, (user_id,))
            user_profile = cur.fetchone()
            return user_profile
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
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

def get_user_stats(user_id):
    """Get simple statistics for a given user."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    ROUND(
                        COALESCE(
                            SUM(
                                EXTRACT(EPOCH FROM (session_ended_at - session_started_at))
                            ) / 60
                        , 0)
                    )::integer as total_surf_time_minutes,
                    ROUND(AVG(fun_rating)::numeric, 2) as average_fun_rating
                FROM surf_sessions_duplicate
                WHERE user_id = %s
            """, (user_id,))
            stats = cur.fetchone()
            return stats
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return None
    finally:
        conn.close()

def get_leaderboard(year=None, stat='sessions'):
    """Get leaderboard data, ranked by a specific statistic."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            params = []
            join_condition = "s ON u.id = s.user_id"

            # If a year is provided, add the condition to the JOIN
            # This is crucial for LEFT JOIN to work correctly and not filter out users
            if year:
                join_condition += " AND EXTRACT(YEAR FROM s.session_started_at) = %s"
                params.append(year)

            # Base query with dynamic join condition
            query = f"""
                SELECT
                    u.id as user_id,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    COUNT(s.id) as total_sessions,
                    ROUND(COALESCE(SUM(EXTRACT(EPOCH FROM (s.session_ended_at - s.session_started_at))) / 60, 0))::integer as total_surf_time_minutes,
                    COALESCE(ROUND(AVG(s.fun_rating)::numeric, 2), 0.0) as average_fun_rating
                FROM auth.users u
                LEFT JOIN surf_sessions_duplicate {join_condition}
                GROUP BY u.id
            """

            # Order by the selected statistic
            if stat == 'time':
                query += " ORDER BY total_surf_time_minutes DESC, total_sessions DESC"
            elif stat == 'rating':
                # For rating, also sort by number of sessions to rank users with 0 sessions fairly
                query += " ORDER BY average_fun_rating DESC NULLS LAST, total_sessions DESC"
            else: # Default to sessions
                query += " ORDER BY total_sessions DESC, total_surf_time_minutes DESC"
            
            query += " LIMIT 100" # Limit to top 100

            cur.execute(query, tuple(params))
            leaderboard_data = cur.fetchall()
            return leaderboard_data

    except Exception as e:
        print(f"Error getting leaderboard data: {e}")
        import traceback
        traceback.print_exc()
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
                    COUNT(CASE WHEN EXTRACT(YEAR FROM session_started_at) = {year} THEN 1 END) as {prefix}_total_sessions,
                    ROUND(
                        (COUNT(CASE WHEN EXTRACT(YEAR FROM session_started_at) = {year} THEN 1 END)::numeric / 
                        {sessions_per_week_divisor})::numeric, 2
                    ) as {prefix}_sessions_per_week,
                    ROUND(
                        AVG(CASE WHEN EXTRACT(YEAR FROM session_started_at) = {year} THEN CAST(fun_rating AS FLOAT) END)::numeric, 2
                    ) as {prefix}_avg_fun_rating,
                    ROUND(
                        AVG(CASE 
                            WHEN EXTRACT(YEAR FROM session_started_at) = {year} AND session_ended_at IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (session_ended_at - session_started_at)) / 60 
                        END)::numeric, 1
                    ) as {prefix}_avg_session_duration_minutes,
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN EXTRACT(YEAR FROM session_started_at) = {year} AND session_ended_at IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (session_ended_at - session_started_at)) / 60 
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
                other_users_yearly_selects.append(_get_yearly_stats_sql(year, f'year_{year}', is_current_year_calc).replace('session_started_at', 's.session_started_at'))

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
                WHERE user_id = %s AND EXTRACT(YEAR FROM session_started_at) = %s
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
                            WHEN session_ended_at IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (session_ended_at - session_started_at)) / 60 
                        END)::numeric, 1
                    ) as avg_session_duration_minutes,
                    
                    -- Total community surf time in minutes (sessions with end_time)
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN session_ended_at IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (session_ended_at - session_started_at)) / 60 
                        END), 0)::numeric, 1
                    ) as total_surf_time_minutes
                    
                FROM surf_sessions_duplicate
                WHERE EXTRACT(YEAR FROM session_started_at) = %s
            """, (current_year,))
            
            community_stats = cur.fetchone()
            
            # 3b. COMMUNITY TOP LOCATION (NEW)
            cur.execute("""
                SELECT location, COUNT(*) as session_count
                FROM surf_sessions_duplicate 
                WHERE EXTRACT(YEAR FROM session_started_at) = %s
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
                    WHERE user_id = %s AND EXTRACT(YEAR FROM session_started_at) = %s
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

def create_session_with_participants(session_data, creator_user_id, tagged_user_ids=None, send_notifications=True):
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
                    # Ensure the tagged user is not the creator themselves
                    # and ensure the tagged_user_id is not None
                    if tagged_user_id and str(tagged_user_id) != str(creator_user_id):
                        cur.execute("""
                            INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                            VALUES (%s, %s, %s, %s)
                            RETURNING *
                        """, (new_session_id, tagged_user_id, creator_user_id, 'tagged_participant'))
                        
                        tagged_participant = cur.fetchone()
                        if tagged_participant:
                            participant_records.append(dict(tagged_participant))
                            # Create a notification for the tagged user only if send_notifications is True
                            if send_notifications:
                                create_notification(
                                    recipient_user_id=tagged_user_id,
                                    sender_user_id=creator_user_id,
                                    session_id=new_session_id,
                                    notification_type='session_tag'
                                )
            
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

def get_session_summary_list(viewer_id, profile_user_id_filter=None, filters={}):
    """Retrieve a filtered list of lightweight session summaries."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Base query with lightweight fields
            query = """
                SELECT 
                    s.id, s.created_at, s.session_name, s.location, s.fun_rating, s.session_notes,
                    s.swell_buoy_id, s.met_buoy_id, s.tide_station_id, s.user_id, s.session_group_id,
                    s.session_started_at, s.session_ended_at,
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
                    ) as shakas,
                    (SELECT COUNT(*) FROM comments WHERE session_id = s.id) as comment_count
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                LEFT JOIN surf_spots sp ON s.location = sp.name
            """
            params = [viewer_id]
            where_clauses = []

            if profile_user_id_filter:
                where_clauses.append("s.user_id = %s")
                params.append(profile_user_id_filter)

            if 'min_swell_height' in filters:
                where_clauses.append("(s.raw_swell->0->'swell_components'->'swell_1'->>'height')::numeric >= %s")
                params.append(filters['min_swell_height'])
            
            if 'max_swell_height' in filters:
                where_clauses.append("(s.raw_swell->0->'swell_components'->'swell_1'->>'height')::numeric <= %s")
                params.append(filters['max_swell_height'])

            if 'min_swell_period' in filters:
                where_clauses.append("(s.raw_swell->0->'swell_components'->'swell_1'->>'period')::numeric >= %s")
                params.append(filters['min_swell_period'])

            if 'max_swell_period' in filters:
                where_clauses.append("(s.raw_swell->0->'swell_components'->'swell_1'->>'period')::numeric <= %s")
                params.append(filters['max_swell_period'])

            if 'swell_direction' in filters:
                direction_map = {
                    'N': (337.5, 22.5),
                    'NNE': (11.25, 33.75),
                    'NE': (33.75, 56.25),
                    'ENE': (56.25, 78.75),
                    'E': (78.75, 101.25),
                    'ESE': (101.25, 123.75),
                    'SE': (123.75, 146.25),
                    'SSE': (146.25, 168.75),
                    'S': (168.75, 191.25),
                    'SSW': (191.25, 213.75),
                    'SW': (213.75, 236.25),
                    'WSW': (236.25, 258.75),
                    'W': (258.75, 281.25),
                    'WNW': (281.25, 303.75),
                    'NW': (303.75, 326.25),
                    'NNW': (326.25, 348.75)
                }
                direction = filters['swell_direction'].upper()
                if direction in direction_map:
                    min_dir, max_dir = direction_map[direction]
                    if direction == 'N':
                        where_clauses.append("((s.raw_swell->0->'swell_components'->'swell_1'->>'direction')::numeric >= %s OR (s.raw_swell->0->'swell_components'->'swell_1'->>'direction')::numeric < %s)")
                    else:
                        where_clauses.append("(s.raw_swell->0->'swell_components'->'swell_1'->>'direction')::numeric BETWEEN %s AND %s")
                    params.extend([min_dir, max_dir])

            if 'region' in filters:
                where_clauses.append("sp.region ILIKE %s")
                params.append(filters['region'])

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY s.session_started_at DESC"

            print(f"DEBUG: get_session_summary_list - profile_user_id_filter: {profile_user_id_filter}, viewer_id: {viewer_id}")
            print(f"DEBUG: get_session_summary_list - SQL Query: {query}")
            print(f"DEBUG: get_session_summary_list - Query Params: {params}")

            cur.execute(query, tuple(params))
            sessions = cur.fetchall()

            return [_format_session_response(s) for s in sessions]

    except Exception as e:
        print(f"Error retrieving lightweight sessions: {e}")
        raise
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
                    s1.id, s1.created_at, s1.session_name, s1.location, s1.fun_rating, s1.session_notes,
                    s1.raw_swell, s1.swell_buoy_id, s1.raw_met, s1.met_buoy_id,
                    s1.tide_station_id, s1.user_id, s1.session_group_id,
                    s1.session_water_level, s1.tide_direction, s1.next_tide_event_type, s1.next_tide_event_at, s1.next_tide_event_height,
                    s1.session_started_at, s1.session_ended_at,
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
                GROUP BY s1.id, s1.created_at, s1.session_name, s1.location, s1.fun_rating, s1.session_notes,
                         s1.raw_swell, s1.swell_buoy_id, s1.raw_met, s1.met_buoy_id,
                         s1.tide_station_id, s1.user_id, s1.session_group_id, u1.email, u1.raw_user_meta_data, s1.session_started_at, s1.session_ended_at
                ORDER BY s1.created_at DESC
            """

            cur.execute(query, (current_user_id, tuple(possible_names)))
            sessions = cur.fetchall()
            sessions_list = list(sessions)

            # Process each session to handle non-serializable types
            for i, session in enumerate(sessions_list):
                # Standardize all timestamp fields to ISO 8601 format
                for field in ['created_at', 'session_started_at', 'session_ended_at', 'next_tide_event_at']:
                    if field in session and isinstance(session[field], datetime):
                        sessions_list[i][field] = session[field].isoformat()

                # Group tide data into a single object
                tide_data = {}
                if 'session_water_level' in session:
                    tide_data['water_level'] = session.pop('session_water_level')
                if 'tide_direction' in session:
                    tide_data['direction'] = session.pop('tide_direction')
                if 'next_tide_event_type' in session:
                    tide_data['next_event_type'] = session.pop('next_tide_event_type')
                if 'next_tide_event_at' in session:
                    tide_data['next_event_at'] = session.pop('next_tide_event_at')
                if 'next_tide_event_height' in session:
                    tide_data['next_event_height'] = session.pop('next_tide_event_height')
                
                sessions_list[i]['tide'] = tide_data

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

def get_all_regions():
    """Retrieve all unique surf regions from the database."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT region 
                FROM surf_spots 
                WHERE region IS NOT NULL AND region <> '' 
                ORDER BY region;
            """)
            regions = [item[0] for item in cur.fetchall()]
            return regions
    except Exception as e:
        print(f"Error retrieving all regions: {e}")
        return []
    finally:
        conn.close()