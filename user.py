# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from pytgcalls import PyTgCalls
from pyrogram import Client
from config import Config
from utils import LOGGER

USER = Client(
    Config.SESSION,
    Config.API_ID,
    Config.API_HASH,
    plugins=dict(root="userplugins")
    )
group_call = PyTgCalls(USER, cache_duration=180)


