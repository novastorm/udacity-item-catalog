import cgi
import re

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from database_setup import Base
from database_setup import Restaurant
from database_setup import MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pprint

pp = pprint.PrettyPrinter(indent=4)

PORT = 8080

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += '''<a href="/restaurants/create">new Restaurant</a><br />'''
                output += "<br />"
                output += "<br />"
                for record in restaurants:
                    output += record.name
                    output += "<br />"
                    output += '''<a href="/restaurants/%s/edit">Edit</a><br />''' % record.id
                    output += '''<a href="/restaurants/%s/confirm-delete">Delete</a><br />'''  % record.id
                    output += "<br />"

                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/create"):
                restaurants = session.query(Restaurant).all()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += '''<form method="POST" enctype="multipart/form-data" action="/restaurants/store">'''
                output += '''<input name="input-restaurant-name" type="text" placeholder="New Restaurant Name">'''
                output += '''<input type="submit" value="Create">'''
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if re.match(r'/restaurants/(\d+)/edit$', self.path, re.I):
                matches = re.match(r'/restaurants/(\d+)/edit$', self.path, re.I)
                print matches.group(1)
                restaurant = session.query(Restaurant).filter_by(id=matches.group(1)).one()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>%s</h1>" % restaurant.name
                output += '''<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/update">''' % restaurant.id
                output += '''<input name="input-restaurant-name" type="text" value="%s">''' % restaurant.name
                output += '''<input type="submit" value="Rename">'''
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if re.match(r'/restaurants/(\d+)/confirm-delete$', self.path, re.I):
                matches = re.match(r'/restaurants/(\d+)/confirm-delete$', self.path, re.I)
                print matches.group(1)
                restaurant = session.query(Restaurant).filter_by(id=matches.group(1)).one()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s?</h1>" % restaurant.name
                output += '''<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/delete">''' % restaurant.id
                output += '''<input type="submit" value="Delete">'''
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/store"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messsageContent = fields.get('input-restaurant-name')
                    # store new restaurant record
                    restaurant = Restaurant(name=messsageContent[0])
                    session.add(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

                return

            if re.match(r'/restaurants/(\d+)/update$', self.path, re.I):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messsageContent = fields.get('input-restaurant-name')
                    pp.pprint(messsageContent)

                    matches = re.match(r'/restaurants/(\d+)/update$', self.path, re.I)
                    restaurant = session.query(Restaurant).filter_by(id=matches.group(1)).one()
                    if restaurant != []:
                        restaurant.name = messsageContent[0]
                        session.add(restaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                return

            if re.match(r'/restaurants/(\d+)/delete$', self.path, re.I):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    matches = re.match(r'/restaurants/(\d+)/delete$', self.path, re.I)
                    restaurant = session.query(Restaurant).filter_by(id=matches.group(1)).one()
                    session.delete(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return

        except:
            pass

def main():
    try:
        server = HTTPServer(('', PORT), webserverHandler)
        print "Web server running on port %s" % PORT
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server ..."
        server.socket.close()

if __name__ == '__main__':
    main()