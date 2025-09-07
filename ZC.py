import hashlib
import json
import time
from datetime import datetime
import qrcode
from PIL import Image
import os

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

class Transaction:
    def __init__(self, sender, recipient, amount, nft_data=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nft_data = nft_data  # NFT metadata (name, description, etc.)
        self.timestamp = time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        transaction_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "nft_data": self.nft_data,
            "timestamp": self.timestamp
        }, sort_keys=True).encode()
        return hashlib.sha256(transaction_string).hexdigest()

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "nft_data": self.nft_data,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

class ZenChain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []
        self.mining_reward = 100
        self.nft_collections = {}

    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        block = Block(len(self.chain), self.pending_transactions, time.time(), self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        
        print("Block successfully mined!")
        self.chain.append(block)
        
        self.pending_transactions = [
            Transaction(None, mining_reward_address, self.mining_reward)
        ]

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for trans in block.transactions:
                if trans.sender == address:
                    balance -= trans.amount
                if trans.recipient == address:
                    balance += trans.amount
        return balance

    def get_transaction_history(self, address):
        history = []
        for block in self.chain:
            for trans in block.transactions:
                if trans.sender == address or trans.recipient == address:
                    history.append(trans.to_dict())
        return history

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True

    def create_nft(self, owner_address, nft_id, nft_name, nft_description):
        if nft_id in self.nft_collections:
            print("NFT already exists!")
            return False
        
        self.nft_collections[nft_id] = {
            "owner": owner_address,
            "name": nft_name,
            "description": nft_description,
            "created_at": time.time()
        }
        
        # Create a transaction for the NFT creation
        nft_transaction = Transaction(
            None,  # System generated
            owner_address,
            0,  # No token transfer
            {"action": "create", "nft_id": nft_id, "name": nft_name, "description": nft_description}
        )
        self.create_transaction(nft_transaction)
        print(f"NFT {nft_id} created successfully!")
        return True

    def transfer_nft(self, sender, recipient, nft_id):
        if nft_id not in self.nft_collections:
            print("NFT does not exist!")
            return False
        
        if self.nft_collections[nft_id]["owner"] != sender:
            print("You don't own this NFT!")
            return False
        
        self.nft_collections[nft_id]["owner"] = recipient
        
        # Create a transaction for the NFT transfer
        nft_transaction = Transaction(
            sender,
            recipient,
            0,  # No token transfer
            {"action": "transfer", "nft_id": nft_id}
        )
        self.create_transaction(nft_transaction)
        print(f"NFT {nft_id} transferred successfully!")
        return True

    def generate_qr_code(self, data, filename="qrcode.png"):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        print(f"QR code saved as {filename}")
        return filename

# CLI Interface for ZenChain
def main():
    zenchain = ZenChain()
    
    # Create some initial addresses
    alice_address = "Alice_Address_123"
    bob_address = "Bob_Address_456"
    miner_address = "Miner_Address_789"
    
    while True:
        print("\n===== ZenChain NFT Blockchain =====")
        print("1. Create Transaction")
        print("2. Mine Pending Transactions")
        print("3. Check Balance")
        print("4. View Transaction History")
        print("5. Create NFT")
        print("6. Transfer NFT")
        print("7. Generate Payment QR Code")
        print("8. Validate Blockchain")
        print("9. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            sender = input("Sender address: ")
            recipient = input("Recipient address: ")
            amount = float(input("Amount: "))
            transaction = Transaction(sender, recipient, amount)
            zenchain.create_transaction(transaction)
            print("Transaction created and added to pending transactions!")
        
        elif choice == "2":
            zenchain.mine_pending_transactions(miner_address)
            print("Mining completed!")
        
        elif choice == "3":
            address = input("Enter address: ")
            balance = zenchain.get_balance(address)
            print(f"Balance for {address}: {balance} ZEN")
        
        elif choice == "4":
            address = input("Enter address: ")
            history = zenchain.get_transaction_history(address)
            print(f"Transaction history for {address}:")
            for tx in history:
                print(f"  {datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} - "
                      f"From: {tx['sender']}, To: {tx['recipient']}, Amount: {tx['amount']} ZEN")
                if tx['nft_data']:
                    print(f"    NFT Action: {tx['nft_data'].get('action', 'N/A')}, "
                          f"NFT ID: {tx['nft_data'].get('nft_id', 'N/A')}")
        
        elif choice == "5":
            owner = input("Owner address: ")
            nft_id = input("NFT ID: ")
            nft_name = input("NFT Name: ")
            nft_description = input("NFT Description: ")
            zenchain.create_nft(owner, nft_id, nft_name, nft_description)
        
        elif choice == "6":
            sender = input("Sender address: ")
            recipient = input("Recipient address: ")
            nft_id = input("NFT ID: ")
            zenchain.transfer_nft(sender, recipient, nft_id)
        
        elif choice == "7":
            address = input("Your address for receiving payment: ")
            amount = input("Amount (optional, press enter to skip): ")
            
            qr_data = {
                "type": "payment",
                "address": address
            }
            
            if amount:
                qr_data["amount"] = float(amount)
            
            filename = f"payment_qr_{int(time.time())}.png"
            zenchain.generate_qr_code(json.dumps(qr_data), filename)
            print(f"Payment QR code generated: {filename}")
            
            # Display the QR code if possible
            try:
                img = Image.open(filename)
                img.show()
            except:
                pass
        
        elif choice == "8":
            is_valid = zenchain.is_chain_valid()
            if is_valid:
                print("Blockchain is valid!")
            else:
                print("Blockchain is invalid!")
        
        elif choice == "9":
            print("Exiting ZenChain. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()