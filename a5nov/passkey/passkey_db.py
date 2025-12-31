# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import sqlite3
import hashlib
import base64
import os
from datetime import datetime


class PasswordVault:
    def __init__(self, db_name='password_vault.db'):
        self.db_name = db_name
        self.master_key = None
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_or_id TEXT NOT NULL,
                encoded_password TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def set_master_key(self, key):
        """Set the master key for encoding/decoding"""
        # Create a deterministic but complex key derivation
        self.master_key = self._create_master_hash(key)

    def _create_master_hash(self, key):
        """Create a master hash from the user's key"""
        # Multi-layer hashing with time-based variation
        timestamp_str = str(
            int(datetime.now().timestamp() // 3600)
        )  # Change every hour
        combined = key + timestamp_str

        # Triple hashing with different algorithms
        sha256_hash = hashlib.sha256(combined.encode()).hexdigest()
        md5_hash = hashlib.md5(sha256_hash.encode()).hexdigest()
        final_hash = hashlib.sha3_512(md5_hash.encode()).hexdigest()

        return final_hash[:32]  # Use first 32 characters as key

    def _creative_encode(self, password, salt):
        """Creative encoding method without external libraries"""
        if not self.master_key:
            raise ValueError('Master key not set!')

        # Step 1: Combine password with salt and master key
        combined = password + salt + self.master_key

        # Step 2: Convert to bytes and apply bit manipulation
        encoded_bytes = combined.encode('utf-8')

        # Step 3: Creative bit rotation and XOR encoding
        result_bytes = bytearray()
        for i, byte in enumerate(encoded_bytes):
            # XOR with master key character (cycling through)
            xor_key = ord(self.master_key[i % len(self.master_key)])
            modified_byte = byte ^ xor_key

            # Bit rotation: rotate left by (i % 7 + 1) bits
            rotation = (i % 7) + 1
            rotated_byte = (
                (modified_byte << rotation) | (modified_byte >> (8 - rotation))
            ) & 0xFF

            result_bytes.append(rotated_byte)

        # Step 4: Reverse the byte array for additional security
        result_bytes.reverse()

        # Step 5: Convert to base64 for storage
        encoded_result = base64.b64encode(result_bytes).decode('utf-8')

        return encoded_result

    def _creative_decode(self, encoded_password, salt):
        """Decode the creatively encoded password"""
        if not self.master_key:
            raise ValueError('Master key not set!')

        # Step 1: Decode from base64
        encoded_bytes = base64.b64decode(encoded_password.encode('utf-8'))

        # Step 2: Reverse the byte array (undo step 4 of encoding)
        reversed_bytes = bytearray(encoded_bytes)
        reversed_bytes.reverse()

        # Step 3: Reverse the bit manipulation
        result_bytes = bytearray()
        for i, byte in enumerate(reversed_bytes):
            # Reverse bit rotation: rotate right by (i % 7 + 1) bits
            rotation = (i % 7) + 1
            unrotated_byte = (
                (byte >> rotation) | (byte << (8 - rotation))
            ) & 0xFF

            # XOR with master key character (same as encoding)
            xor_key = ord(self.master_key[i % len(self.master_key)])
            original_byte = unrotated_byte ^ xor_key

            result_bytes.append(original_byte)

        # Step 4: Convert back to string and extract original password
        combined_string = result_bytes.decode('utf-8', errors='ignore')

        # The original password is everything before the salt
        salt_start = combined_string.find(salt)
        if salt_start == -1:
            raise ValueError('Invalid encoded password or salt mismatch')

        original_password = combined_string[:salt_start]
        return original_password

    def _generate_salt(self):
        """Generate a random salt"""
        return base64.b64encode(os.urandom(16)).decode('utf-8')[:16]

    def add_password(self, url_or_id, password):
        """Add a new password entry"""
        salt = self._generate_salt()
        encoded_password = self._creative_encode(password, salt)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO passwords (url_or_id, encoded_password, salt)
            VALUES (?, ?, ?)
        """,
            (url_or_id, encoded_password, salt),
        )

        conn.commit()
        conn.close()
        print(f"Password for '{url_or_id}' added successfully!")

    def get_password(self, url_or_id):
        """Retrieve and decode a password"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT encoded_password, salt FROM passwords 
            WHERE url_or_id = ?
        """,
            (url_or_id,),
        )

        result = cursor.fetchone()
        conn.close()

        if result:
            encoded_password, salt = result
            try:
                decoded_password = self._creative_decode(
                    encoded_password, salt
                )
                return decoded_password
            except ValueError as e:
                print(f'Error decoding password: {e}')
                return None
        else:
            print(f"No password found for '{url_or_id}'")
            return None

    def update_password(self, url_or_id, new_password):
        """Update an existing password"""
        salt = self._generate_salt()
        encoded_password = self._creative_encode(new_password, salt)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE passwords 
            SET encoded_password = ?, salt = ?, updated_at = CURRENT_TIMESTAMP
            WHERE url_or_id = ?
        """,
            (encoded_password, salt, url_or_id),
        )

        if cursor.rowcount == 0:
            print(f"No password found for '{url_or_id}'")
        else:
            print(f"Password for '{url_or_id}' updated successfully!")

        conn.commit()
        conn.close()

    def delete_password(self, url_or_id):
        """Delete a password entry"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            'DELETE FROM passwords WHERE url_or_id = ?', (url_or_id,)
        )

        if cursor.rowcount == 0:
            print(f"No password found for '{url_or_id}'")
        else:
            print(f"Password for '{url_or_id}' deleted successfully!")

        conn.commit()
        conn.close()

    def list_all_entries(self):
        """List all stored password entries"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT url_or_id, created_at, updated_at FROM passwords 
            ORDER BY url_or_id
        """)

        entries = cursor.fetchall()
        conn.close()

        if entries:
            print('\nStored Password Entries:')
            print('-' * 50)
            for url, created, updated in entries:
                print(f'URL/ID: {url}')
                print(f'Created: {created}, Last Updated: {updated}')
                print('-' * 30)
        else:
            print('No password entries found.')

    def change_master_key(self, new_key):
        """Change master key and re-encode all passwords"""
        if not self.master_key:
            raise ValueError('Current master key not set!')

        # Store current master key temporarily
        old_master_key = self.master_key

        # Get all passwords with old key
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT url_or_id, encoded_password, salt FROM passwords'
        )
        entries = cursor.fetchall()
        conn.close()

        # Set new master key
        self.set_master_key(new_key)

        # Re-encode all passwords with new key
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for url_or_id, encoded_password, old_salt in entries:
            # Temporarily use old key to decode
            self.master_key = old_master_key
            try:
                decoded_password = self._creative_decode(
                    encoded_password, old_salt
                )
            except ValueError:
                print(f'Failed to decode password for {url_or_id}. Skipping.')
                continue

            # Use new key to encode
            self.master_key = self._create_master_hash(new_key)
            new_salt = self._generate_salt()
            new_encoded_password = self._creative_encode(
                decoded_password, new_salt
            )

            # Update in database
            cursor.execute(
                """
                UPDATE passwords 
                SET encoded_password = ?, salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE url_or_id = ?
            """,
                (new_encoded_password, new_salt, url_or_id),
            )

        conn.commit()
        conn.close()
        print(
            'Master key changed successfully! All passwords have been re-encoded.'
        )


def main():
    vault = PasswordVault()

    print('=== Personal Password Vault ===')
    print(
        'Set your master key first (this will be used to encode/decode all passwords)'
    )

    # Set master key
    while True:
        master_key = input('Enter master key: ').strip()
        if master_key:
            vault.set_master_key(master_key)
            break
        else:
            print('Master key cannot be empty!')

    while True:
        print('\nOptions:')
        print('1. Add new password')
        print('2. Get password')
        print('3. Update password')
        print('4. Delete password')
        print('5. List all entries')
        print('6. Change master key')
        print('7. Exit')

        choice = input('Choose an option (1-7): ').strip()

        if choice == '1':
            url = input('Enter URL or ID: ').strip()
            password = input('Enter password: ').strip()
            vault.add_password(url, password)

        elif choice == '2':
            url = input('Enter URL or ID: ').strip()
            password = vault.get_password(url)
            if password:
                print(f'Password: {password}')

        elif choice == '3':
            url = input('Enter URL or ID: ').strip()
            new_password = input('Enter new password: ').strip()
            vault.update_password(url, new_password)

        elif choice == '4':
            url = input('Enter URL or ID to delete: ').strip()
            vault.delete_password(url)

        elif choice == '5':
            vault.list_all_entries()

        elif choice == '6':
            new_key = input('Enter new master key: ').strip()
            if new_key:
                vault.change_master_key(new_key)
            else:
                print('New master key cannot be empty!')

        elif choice == '7':
            print('Goodbye!')
            break

        else:
            print('Invalid option. Please try again.')


if __name__ == '__main__':
    main()
