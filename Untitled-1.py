class BarScanner:
    def __init__(self):
        self.services = {
            "internet": 5.00,
            "scan": 1.50,
            "print": 0.50,
            "photocopy": 0.75,
            "typing": 2.00,
            "passport photo": 8.00
        }
    
    def scan_item(self, item):
        if item.lower() in self.services:
            return self.services[item.lower()]
        else:
            print("Service not found. Please try again.")
            return 0.00

def main():
    scanner = BarScanner()
    total_amount = 0.00

    print("Welcome to the Bar Scanner!")
    print("Please scan items or type 'done' to finish.")

    while True:
        item = input("Scan item: ")
        if item.lower() == 'done':
            break
        amount = scanner.scan_item(item)
        total_amount += amount

    print(f"Total amount due: ${total_amount:.2f}")

if __name__ == "__main__":
    main()
