# returns all notifications to be backfilled for 12/18/25 slapp update release

from database_utils import get_db_connection
import psycopg2.extras

def dry_run_backfill():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Query to find tagged participants who do NOT have a corresponding notification.
            # We join with auth.users twice (once for recipient, once for sender) to get friendly names.
            query = """
                SELECT 
                    sp.user_id as recipient_id,
                    COALESCE(
                        recipient_u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(recipient_u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(recipient_u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(recipient_u.email, '@', 1)
                    ) as recipient_name,
                    sp.tagged_by_user_id as sender_id,
                    COALESCE(
                        sender_u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(sender_u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(sender_u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(sender_u.email, '@', 1)
                    ) as sender_name,
                    sp.session_id,
                    s.session_name,
                    s.location,
                    s.session_started_at
                FROM session_participants sp
                JOIN surf_sessions_duplicate s ON sp.session_id = s.id
                JOIN auth.users recipient_u ON sp.user_id = recipient_u.id
                JOIN auth.users sender_u ON sp.tagged_by_user_id = sender_u.id
                LEFT JOIN notifications n ON (
                    n.recipient_user_id = sp.user_id 
                    AND n.session_id = sp.session_id 
                    AND n.type = 'session_tag'
                )
                WHERE sp.role = 'tagged_participant'
                AND n.id IS NULL
                ORDER BY s.session_started_at DESC;
            """
            
            print("Querying for missing notifications...")
            cur.execute(query)
            rows = cur.fetchall()
            
            if not rows:
                print("No missing notifications found! All tagged users have notifications.")
                return

            print(f"\nFound {len(rows)} missing notifications that need to be created:\n")
            # Table Header
            print(f"{ 'SENDER':<20} | { 'RECIPIENT':<20} | { 'SESSION ID':<10} | { 'DATE':<12} | { 'SESSION NAME'}")
            print("-" * 110)
            
            for row in rows:
                date_str = row['session_started_at'].strftime('%Y-%m-%d') if row['session_started_at'] else "N/A"
                # Truncate names if they are too long for the column
                sender = (row['sender_name'] or "Unknown")[:18]
                recipient = (row['recipient_name'] or "Unknown")[:18]
                session_name = (row['session_name'] or "Untitled")
                
                print(f"{sender:<20} | {recipient:<20} | {str(row['session_id']):<10} | {date_str:<12} | {session_name}")

            print("-" * 110)
            print(f"\nTotal pending notifications: {len(rows)}")
            print("\nThis was a DRY RUN. No changes were made to the database.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    dry_run_backfill()
