# fb-crawler
![Static Badge](https://img.shields.io/badge/build-passing-brightgreen?style=flat)
![Static Badge](https://img.shields.io/badge/sanity-fading-orangered?style=flat)
![Static Badge](https://img.shields.io/badge/works%3F-barely-rebeccapurple?style=flat)

"Simple" messenger crawler that attempts its very best to rip off messages off https://www.messenger.com/.
Made for the sole purpose of filtering out chats from people that dont know what "exclusively for official communication" means,
even though this doesnt do that. (TODO)

> This actually taught me alot about docker and selenium. Even if its surface level knowledge keeping the dunnning-kreuger effect in mind.

## How to run
1. Export cookies from messenger in JSON format and put it in `src/secrets/messenger-client-cookies.js` or somewhere else
2. Create .env file with `MESSENGERCOOKIE=insert/path/to/cookies.js`
3. Run `docker build -t [INSERT_IMAGE_NAME] .` to build image and run with `docker run [INSERT_IMAGE_NAME]`

OR

1. Simply run `py src/crawler.py` on the root directory, make sure you have installed all dependencies using `pip install -r requirements.txt` and have chrome installed (duh)

> [!NOTE]
> All of the configurations (discord webhook style, channelID, behavior) is already preset, to change their behavior use the crawler.py as reference and make your own crawler.

> [!WARNING]
> Don't make the dumb mistake of pushing with your cookies inside your json file.

## Limitations
+ Originally wanted to run this on https://render.com/, but this program goes past their 512m free limit regularly. Even with experiments with ChatGPT on arguments for browser.
+ Relies too much on waiting for an arbitary amount of time waiting for elements to load since it loads dynamically, just re-run it or get a better signal if it fails.

## Final notes
IF you ever find my cookies in the push history please dont use it, I did invalidate it but just please dont.

###### project made in collaboration with cs1a @ USTP
