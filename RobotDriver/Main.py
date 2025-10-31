import argparse, sys
from RobotDriver.Core.Session import BrowserSession
from RobotDriver.Service.Login import AuthService
from RobotDriver.Service.ProductPrice import CatalogService
from RobotDriver.Site.AutomationExercise import AutomationExerciseAdapter

"""
1. Open a browser
2. Navigate to the site
3. Log-in (sign-up and log-in if account required)
4. Search/Extract for a product and its price
5. Print the result
"""
def main():
    ap = argparse.ArgumentParser(description="Login → Search → Report price")
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--product", "-p", default="Blue Top")
    ap.add_argument("--headful", action="store_true")
    ap.add_argument("--signup-if-needed", action="store_true", dest="auto_signup")
    args = ap.parse_args()

    adapter = AutomationExerciseAdapter()

    with BrowserSession(headless=not args.headful) as s:
        # Home
        adapter.goto_home(s.page)

        # Authenticate
        if not AuthService(adapter, s.page).login(args.email, args.password, auto_signup=args.auto_signup):
            print("Fail: Login failed.")
            sys.exit(2)

        # Search for a product and find its price
        found, price = CatalogService(adapter, s.page).price_for(args.product)
        if found and price:
            print(f'Success! "{args.product}" price is {price}')
            sys.exit(0)
        elif found:
            print(f'Fail: price not found for "{args.product}"')
            sys.exit(2)
        else:
            print(f'Fail: product not found -> "{args.product}"')
            sys.exit(2)

if __name__ == "__main__":
    main()