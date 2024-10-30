import csv
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq, Request

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")  # folder name will be templates


# route to show the review comments in a web UI
@app.route('/search', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ", "")
            flipkart_url = 'https://www.flipkart.com/search?q=' + searchstring
            # uClient = uReq(flipkart_url)
            # flipkartpage = uClient.read()
            # uClient.close()
            # flipkart_html = bs(flipkartpage, "html.parser")
            # bigboxes = flipkart_html.select("._1AtVbE Colin")
            # req = Request(flipkart_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            #                                      'Accept-Language': 'en-US,en;q=0.9',
            #                                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            #                                      'Connection': 'keep-alive',
            #                                      })
            req = Request(
                flipkart_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.flipkart.com/'
                }
            )

            uClient = uReq(req)
            # Read the page content
            page_html = uClient.read()
            # Close the connection
            uClient.close()
            # Process or print page_html
            print(page_html)
            flipkart_html = bs(page_html, "html.parser")
            bigboxes = flipkart_html.findAll(
                "div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            product_link = "https://www.flipkart.com" + \
                box.div.div.div.a['href']
            prodRes = requests.get(product_link, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Referer': 'https://www.flipkart.com/'
            })
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            # check console
            # print(prodRes)
            # print(product_link)
            commentboxes = prod_html.findAll("div", {"class": "RcXBOT"})
            filename = searchstring + ".csv"
            fw = open(filename, 'w')
            headers = "Products, Customer Name, Rating, Heading, Comments \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = name = commentbox.div.div.find_all(
                        'p', {'class': '_2NsDsF AwS1CA'})[0].text
                except:
                    name = 'No Name'
                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'
                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)
                mydict = {"Product": searchstring, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template("index.html")


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
