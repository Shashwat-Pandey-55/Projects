<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Muyoouu/stockmarket-webapp">
    <img src="static/favicon.ico" alt="Logo" width="120" height="120">
  </a>

<h3 align="center">stockmarket-webapp</h3>

  <p align="center">
    Stock market simulator in form of web application, built in Python-Flask
    <br />
    <br />
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://stocksims.pythonanywhere.com/)

Web application built in Flask-app, simulate stock-trading experience in stock-market.  
Using real-time data provided by [Alpha Vantage](https://www.alphavantage.co/) Free API, this app can simulate stock-market experience.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python.py]][Python-url]
* [![Flask][Flask.py]][Flask-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![SQLite][SQLite.db]][SQLite-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* pip
  ```bash
  apt-get install python3-pip
  ```
* python 3.10

### Installation

1. Get a free API Key at [https://www.alphavantage.co/](https://www.alphavantage.co/)
2. Clone the repo
   ```bash
   git clone https://github.com/Muyoouu/stockmarket-webapp.git
   ```
3. Install pip packages
   ```bash
   pip install -r /path/to/requirements.txt
   ```
4. Export your API KEY in terminal to create environment variable
   ```bash
   export API_KEY='ENTER YOUR API KEY'
   ```
5. Run your Flask app in local using this command
   ```bash
   flask run
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

For starters, user should register a username-password in register page. After signed-in, user will be redirected to main page which will show user stock portofolios (if any).  
Also there are features user can access, several feature available currently are:

* Quote - provide current stock price
* Buy - add stock to user portofolios (using mock-up cash balance)
* Sell - sell stock from user portofolios (adding mock-up cash balance)
* History - provide history of transactions done by user

Video Demo:  <https://youtu.be/g4sKowr7SDI>  
For more details, check out the web-app: [https://stocksims.pythonanywhere.com/](https://stocksims.pythonanywhere.com/)

<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE.txt`](LICENSE.txt) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Musa Yohanes - musayohanes00@gmail.com

Project Link: [https://github.com/Muyoouu/stockmarket-webapp](https://github.com/Muyoouu/stockmarket-webapp)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* This project initially was an assignment from learning course [CS50](https://cs50.harvard.edu/x/2023/psets/9/finance/). Which provide the ideas and guides for the app development.
* Real-time stock data provided by [Alpha Vantage](https://www.alphavantage.co/) API.
* Credits to the README file template provided by [Best-README-Template](https://github.com/othneildrew/Best-README-Template), very helpful!

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: img/Screenshot_Portofolio_Page.png
[Python.py]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[Flask.py]: https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/2.3.x/
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[SQLite.db]: https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://sqlite.org/