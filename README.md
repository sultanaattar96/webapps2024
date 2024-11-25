# Project Title - Django Online Payment System

### Installing

$ pip install djangorestframework

$ pip install django-money

$ pip install psycopg2

$ pip install social-auth-app-django

$ pip install requests

$ pip install pillow

$ pip install thrift thriftpy2

$ python manage.py createsuperuser --username admin1 --email admin1@example.com

$ py manage.py makemigrations

$ python manage.py migrate

$ python manage.py runserver

sudo apt install postgresql postgresql-contrib

## Project working details

User Registration: Users can register by providing essential information such as username, name, email, and password. They select the currency for their online account during registration. Each user has a single online account whose currency (GB Pounds, US dollars, or Euros) is selected upon registration. The system makes the appropriate conversion to assign the right initial amount of money.

<img src="/ImagesSS/1.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/2.png" alt="Screenshot of Application" width="500"/>

To register, a user must provide:
Username

First and last name

Email address

Password

<img src="/ImagesSS/3.png" alt="Screenshot of Application" width="500"/>


Username Uniqueness: The system checks if the entered username already exists in the database. If it does, it displays the error message: “A user with that username already exists.”
Email Uniqueness: Similarly, the system checks if the entered email is already associated with an existing account. If it is, it displays the error message: “User with this Email already exists.”
Password Strength: The system checks the length of the entered password. If the password is less than 8 characters long, it displays the error message: “This password is too short. It must contain at least 8 characters.”

These types of validations have been added on each page to maintain the system. Validation checks help ensure that each user has a unique username and email, and that their password is sufficiently strong. This is crucial for maintaining the integrity and security of user accounts on the website.

Login:

<img src="/ImagesSS/4.png" alt="Screenshot of Application" width="500"/>


The dashboard is a part of a Django web application. Django follows the ModelViewTemplate architectural pattern, and this dashboard is constructed using these components:

 Models: The data shown on the dashboard (like the account balance and notifications) is stored in database tables. In Django, the structure of these tables is defined by classes in `models.py`.

 Views: The logic for fetching this data and deciding what to show on the dashboard is in a `views.py`. This view would query the models for data and pass this data to the template.

 Templates: The visual structure of the dashboard is defined in a template file (HTML). This template defines how data passed in from the view is displayed. It also defines the actions a user can take, like transferring money or requesting payment.

 URLs: Each action the user can take from the dashboard corresponds to a different URL in the application. The mapping from URLs to views is defined in `urls.py`.

 <img src="/ImagesSS/5.png" alt="Screenshot of Application" width="500"/>

 FrontEnd: The frontend of the dashboard, including the interactive icons and visual design, is likely implemented using HTML and CSS. 

 Middleware: If the application includes features like session handling, or CSRF protection.

Transfer Money: Users have the capability to transfer funds seamlessly between their online accounts. This allows for convenient management of finances, enabling users to allocate funds as needed. Additionally, users can initiate direct payments to other individuals, facilitating quick and efficient transactions.

<img src="/ImagesSS/6.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/7.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/8.png" alt="Screenshot of Application" width="500"/>

Requesting Money: Users also have the option to request payments from other users within the system. This feature is particularly useful for situations where a user needs to collect funds from another party, such as repayment for goods or services rendered. By initiating a payment request, users can streamline the process of receiving funds, enhancing overall transaction efficiency.

<img src="/ImagesSS/9.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/10.png" alt="Screenshot of Application" width="500"/>

When a user requests money, it creates a new PaymentRequest object in the database. This object stores information about the request, like the amount, the user who requested it , and the user from whom money is requested.

Users can check for notifications regarding payments and payment requests in their accounts.

<img src="/ImagesSS/11.png" alt="Screenshot of Application" width="500"/>

Notifications: Once the PaymentRequest is created, a notification is generated for the recipient. The request is stored in the PaymentRequest database. If the recipient approves it, a transaction is created. If rejected, the status is updated accordingly. The notification then appears in the recipient's "Notifications" section on their dashboard.

<img src="/ImagesSS/12.png" alt="Screenshot of Application" width="500"/>

Approve or Reject: When the requester views the notification, they could be given options to approve or reject the request. These would be dropdowns that send a POST request to a Django view. This view would then update the PaymentRequest object to mark it as approved or rejected.

<img src="/ImagesSS/13.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/14.png" alt="Screenshot of Application" width="500"/>

Update Balance: If the requester approves the payment request, the view could also update the account balances of both users. It would decrease the balance of the requester and increase the balance of the requester by the requested amount.

<img src="/ImagesSS/15.png" alt="Screenshot of Application" width="500"/>

Transaction History: Users can view their transaction history, including sent and received payments, and payment requests.

<img src="/ImagesSS/16.png" alt="Screenshot of Application" width="500"/>

Users who initiated the request can track the approval status of other users through the "Payment You Requested" page.

<img src="/ImagesSS/17.png" alt="Screenshot of Application" width="500"/>

Once the request is approved, it will be clearly visible in the screenshots that the amount for both users has been updated.

<img src="/ImagesSS/18.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/19.png" alt="Screenshot of Application" width="500"/>

During money transfers, if a user selects a currency that is different from both the sender's and receiver's currencies, it can complicate storage. Therefore, proper validation has been added to handle this scenario effectively.

<img src="/ImagesSS/20.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/21.png" alt="Screenshot of Application" width="500"/>

Administrator Access: A default admin1 account has been created, granting access to create new admin accounts, view all transactions, all accounts, and all payment requests along with their statuses.

<img src="/ImagesSS/22.png" alt="Screenshot of Application" width="500"/>

Only admins have the authority to perform these actions.

<img src="/ImagesSS/23.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/24.png" alt="Screenshot of Application" width="500"/>

<img src="/ImagesSS/25.png" alt="Screenshot of Application" width="500"/>

All account list:

<img src="/ImagesSS/26.png" alt="Screenshot of Application" width="500"/>

All payment request list:

<img src="/ImagesSS/27.png" alt="Screenshot of Application" width="500"/>

All transaction list:

<img src="/ImagesSS/28.png" alt="Screenshot of Application" width="500"/>

Currency Conversion: A separate RESTful web service handles currency conversion using statically assigned exchange rates.

<img src="/ImagesSS/29.png" alt="Screenshot of Application" width="500"/>

