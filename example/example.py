import pywebex.webex as web

rawr=web.WebEx('WebExId','PASSWORD', 'SITENAME','EMAIL')


#try to execute the query, if there's an exception from webex, take necessary action
try:
    query=rawr.getEvent({'key': '11111'})
    print query
except WebExException as e:
    print e




