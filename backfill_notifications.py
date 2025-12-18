# backfills notifications for 12/18/25 slapp update release


from database_utils import get_db_connection, create_notification
import psycopg2.extras

def run_backfill():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Query to find tagged participants who do NOT have a corresponding notification.
            query = """
                SELECT 
                    sp.user_id as recipient_id,
                    sp.tagged_by_user_id as sender_id,
                    sp.session_id,
                    s.session_name
                FROM session_participants sp
                JOIN surf_sessions_duplicate s ON sp.session_id = s.id
                LEFT JOIN notifications n ON (
                    n.recipient_user_id = sp.user_id 
                    AND n.session_id = sp.session_id 
                    AND n.type = 'session_tag'
                )
                WHERE sp.role = 'tagged_participant'
                AND n.id IS NULL;
            """
            
            print("Querying for missing notifications...")
            cur.execute(query)
            rows = cur.fetchall()
            
            if not rows:
                print("No missing notifications found! All tagged users have notifications.")
                return

            print(f"Found {len(rows)} missing notifications. Creating them now...\n")
            
            count = 0
            for row in rows:
                # Use the existing utility function to ensure consistency
                result = create_notification(
                    recipient_user_id=row['recipient_id'],
                    sender_user_id=row['sender_id'],
                    session_id=row['session_id'],
                    notification_type='session_tag'
                )
                
                if result:
                    count += 1
                    print(f"[{count}/{len(rows)}] Created notification for Session {row['session_id']} ('{row['session_name']}')")
                else:
                    print(f"Failed to create notification for Session {row['session_id']}")

            print(f"\nSuccess! Backfilled {count} notifications.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_backfill()
