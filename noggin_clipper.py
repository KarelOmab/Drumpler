from noggin import Noggin
from constants import NOGGIN_URL, NOGGIN_PORT, NOGGIN_DEBUG

app = Noggin(host=NOGGIN_URL, port=NOGGIN_PORT, debug=NOGGIN_DEBUG)
app.run()