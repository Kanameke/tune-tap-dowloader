# Tune Tap DLC Downloader

A small static website (GitHub Pages ready) that hosts and downloads **Tune Tap Simulator** DLC song packs. It is the companion to the **tunetap-simulator** repo (the game).

Every song is its own `custom_song_*.zip`, and **all of them live together in one folder: `songs/`**. Packs are just lists of file names, so a song can be in several packs and nothing is ever moved around.

**Contents**
[How to download songs](#how-to-download-songs) · [How the site works](#how-the-site-works) · [Host it](#host-it) · [Add songs and packs](#add-songs-and-packs) · [The code](#the-code) · [File list](#files-that-go-in-songs) · [Troubleshooting](#troubleshooting)

---

## How to download songs

1. Open the site. Each pack is a card with its announcement picture, how many songs are available and two buttons.
2. **Download pack (.zip)** bundles every available song of that pack into one zip (named after the pack). Unzip it, you get the individual `custom_song_*.zip` files.
3. **Song list** opens the songs of the pack. Each row has the title, artist, level and a **Download** button for that one song. Use the search box to filter every pack by song, artist or pack name.
4. Open **Tune Tap Simulator**, tap **＋** in the song list and select the downloaded `custom_song_*.zip` files. **Do not unzip those**; the game reads them as they are.

You can also skip the website: the raw zips are in this repo's `songs/` folder.

## How the site works

There is no backend. The page is static HTML plus JavaScript:

1. It loads `dlc.json`, a generated index of every pack and song.
2. For each listed song it sends a `HEAD` request to `songs/<file>`. If the zip exists the song is marked available, so a zip you just uploaded shows up even before `dlc.json` is rebuilt.
3. A song's **Download** button is a plain link with the `download` attribute pointing at `songs/<file>`.
4. **Download pack** fetches each available zip, adds it to a [JSZip](https://stuk.github.io/jszip/) archive in the browser (stored, no recompression) and offers the result as a download. JSZip is loaded from cdnjs; if it fails to load, the per-song buttons still work.
5. `tools/build_index.py` (run by a GitHub Action on every push) regenerates `dlc.json` from `packs/*/pack.json` plus whatever zips are present in `songs/`.

```
index.html                  the downloader page (HTML + CSS + JS, no build)
dlc.json                    generated index, do not edit by hand
songs/                      ALL song zips, one flat folder
  FILES.md                  checklist of every file that belongs here
tools/build_index.py        rebuilds dlc.json
.github/workflows/          rebuilds dlc.json on pushes to songs/ or packs/
packs/
  order.json                the order packs are shown in
  <pack-id>/
    pack.json               title, description, which zips belong to the pack
    banner.jpg              the announcement picture (16:9)
```

## Host it

```bash
python3 -m http.server 8000      # preview locally, then open http://localhost:8000
```

(Opening `index.html` straight from disk will not work because it loads `dlc.json`.)

To publish: create a GitHub repo, push this folder, then **Settings → Pages → Build and deployment → Deploy from a branch → `main` / root**. The site is at `https://<you>.github.io/<repo>/`.

Then put that URL into the game's `index.html`:

```js
const DLC_SITE='https://<you>.github.io/<repo>/';
```

## Add songs and packs

**Add a song to an existing pack**

1. Copy the zip into `songs/`.
2. Push. The Action rebuilds `dlc.json`. (Or run `python3 tools/build_index.py` yourself.)

A zip that no pack lists is still picked up: the script opens its `manifest.json` and shows it under an automatic **Other songs** pack. To group it properly, add it to a `pack.json`.

**Add a new pack**

1. Copy a folder in `packs/` and rename it (lowercase, no spaces, e.g. `sparklink-stars-vol2`).
2. Edit its `pack.json`:

```json
{
  "id": "sparklink-stars-vol2",
  "title": "Disney Sparklink Stars Vol. 2",
  "description": "Second Sparklink Stars pack.",
  "banner": "banner.jpg",
  "status": "ready",
  "note": "",
  "songs": [
    { "file": "custom_song_12345.zip", "title": "Song Name", "jp": "", "artist": "Artist", "level": 10 }
  ]
}
```

3. Replace `banner.jpg` with your announcement picture.
4. Add the id to `packs/order.json` (unlisted packs are shown last).
5. Drop the zips into `songs/` and push.

## The code

**`dlc.json`** (generated) is `{ "generated": "...", "packs": [ <pack.json plus "count", "available" and per-song "available", "size"> ] }`.

**`tools/build_index.py`** in short:

```python
PRESENT = {f for f in os.listdir(SONGS) if f.endswith('.zip')}       # zips on disk
for pid in order:                                                    # each pack, in order.json order
    pj = json.load(open(f'packs/{pid}/pack.json'))
    for s in pj['songs']:
        s['available'] = s['file'] in PRESENT
        s['size'] = os.path.getsize(f'songs/{s["file"]}') if s['available'] else 0
extra = PRESENT - claimed                                            # zips no pack lists
# ...each extra zip: read manifest.json and add it to an "Other songs" pack
json.dump(out, open('dlc.json', 'w'))
```

**Checking a zip from the command line**

```python
import zipfile, json
z = zipfile.ZipFile('songs/custom_song_10145.zip')
print(z.namelist())                              # manifest.json, audio, jacket, chart_1..4.json
print(json.loads(z.read('manifest.json'))['name_en'])
```

**The Action** (`.github/workflows/build-index.yml`) runs on pushes that touch `packs/**` or `songs/**`, runs the script and commits `dlc.json` back if it changed.

## Files that go in `songs/`

**All 87 song zips are already in `songs/`** (69 custom songs plus the 18 MyGO!!!!! / CRYCHIC and Ave Mujica songs). Use this list to check nothing is missing; `songs/FILES.md` has the same list.

### MyGO!!!!! DLC Song Pack (7 files)
- [x] `custom_song_mygo_01_haruhikage.zip`: Haruhikage
- [x] `custom_song_mygo_02_hekitenbansou.zip`: HekitenBansou
- [x] `custom_song_mygo_03_hitoshizuku.zip`: Hitoshizuku
- [x] `custom_song_mygo_04_i_want_to_be_your_heart.zip`: I want to be your heart
- [x] `custom_song_mygo_05_mayoiuta.zip`: Mayoiuta
- [x] `custom_song_mygo_06_non_breath_oblige_cover.zip`: Non-Breath Oblige (Cover)
- [x] `custom_song_mygo_07_silhouette_dance.zip`: Silhouette Dance

### Ave Mujica DLC Song Pack (11 files)
- [x] `custom_song_am_01_ave_mujica.zip`: Ave Mujica
- [x] `custom_song_am_02_black_birthday.zip`: Black Birthday
- [x] `custom_song_am_03_georgette_me_georgette_you.zip`: Georgette Me, Georgette You
- [x] `custom_song_am_04_imprisoned_xii.zip`: Imprisoned XII
- [x] `custom_song_am_05_alter_ego_kao.zip`: Alter Ego (Kao)
- [x] `custom_song_am_06_killkiss.zip`: KiLLKiSS
- [x] `custom_song_am_07_masquerade_rhapsody_request.zip`: Masquerade Rhapsody Request
- [x] `custom_song_am_08_sora_no_musica.zip`: Sora no Musica
- [x] `custom_song_am_09_abracadabra_cover.zip`: Abracadabra (Cover)
- [x] `custom_song_am_10_in_your_blue_eyes.zip`: in your blue eyes
- [x] `custom_song_am_11_zankoku_na_tenshi_no_thesis_ave_mujica_ver.zip`: Zankoku na Tenshi no Thesis (Ave Mujica Ver.)

### Roselia DLC Song Pack (8 files)
- [x] `custom_song_10145.zip`: New Genesis
- [x] `custom_song_10137_1.zip`: Six Trillion Years and One Night Story
- [x] `custom_song_10151_1.zip`: Blessing Chord
- [x] `custom_song_10513.zip`: Red Fraction (Cover)
- [x] `custom_song_10514.zip`: Synchrogazer (Cover)
- [x] `custom_song_10576.zip`: Bad Apple!! (feat. nomico) (Cover)
- [x] `custom_song_10099_1.zip`: [FULL] Fire Bird
- [x] `custom_song_10502_1.zip`: [FULL] FIRE BIRD (10th anniv. ver.)

### Twisted-Wonderland Vol. 1 (11 files)
- [x] `custom_song_10372_1.zip`: Piece of my World (Animation Ver.)
- [x] `custom_song_10410_1.zip`: RED HEART RAGE
- [x] `custom_song_10468_1.zip`: ggwp
- [x] `custom_song_10477_2.zip`: Blessing
- [x] `custom_song_10500.zip`: Yoru ni Kakeru (Seiichiro Yamashita Ver.)
- [x] `custom_song_10503.zip`: Otome Dissection (N-kun Ver.)
- [x] `custom_song_10537.zip`: KING (Nobuhiko Okamoto Ver.)
- [x] `custom_song_10540_1.zip`: RAVE-UP! UP!
- [x] `custom_song_10546.zip`: Obedience
- [x] `custom_song_10554.zip`: Absolutely Beautiful
- [x] `custom_song_10556.zip`: Piece of my World (NRC Ver.)

### Release DLC Pack Vol. 1 (6 files)
- [x] `custom_song_10584_1.zip`: Gira Galactic・Tightrope
- [x] `custom_song_10616.zip`: Abyss
- [x] `custom_song_10633_1.zip`: Door to Summer (Never end ver.)
- [x] `custom_song_10635_1.zip`: KIZUNA MUSIC♪
- [x] `custom_song_10636.zip`: Tanebi
- [x] `custom_song_10637_1.zip`: Toy Doll (Setsuna Yuki Ver.)

### Release DLC Pack Vol. 2 (14 files)
- [x] `custom_song_10631.zip`: START!! True dreams
- [x] `custom_song_10631_liella.zip`: START!! True dreams (Liella! Ver.)
- [x] `custom_song_10621.zip`: Hai Yorokonde (Cover)
- [x] `custom_song_10580.zip`: Kyouran Hey Kids!!
- [x] `custom_song_10549.zip`: Stellar Stellar (millsage ver.)
- [x] `custom_song_10551.zip`: Six Trillion Years and One Night Story (Mugendai MewType Ver.)
- [x] `custom_song_10542.zip`: DIADEM
- [x] `custom_song_10497_1.zip`: First Step
- [x] `custom_song_10475_1.zip`: Bling-Bang-Bang-Born
- [x] `custom_song_10448.zip`: Kyuukurarin
- [x] `custom_song_10439.zip`: Kimi no Kokoro wa Kagayaiteru Kai? (Cover)
- [x] `custom_song_10377_1.zip`: Wish Song ～11 Ver.～
- [x] `custom_song_10183_1.zip`: Kimeta yo Hand in Hand (Kimi to Idol Precure♪ Ver.)
- [x] `custom_song_10142.zip`: God-ish

### Disney Sparklink Stars Vol. 1 (4 files)
- [x] `custom_song_10582_1.zip`: We can dream it, We can do it!!
- [x] `custom_song_10566_1.zip`: UTAGE
- [x] `custom_song_10567_1.zip`: feuillemort
- [x] `custom_song_10564_2.zip`: One and Only

### Persona Series DLC Song Pack (3 files)
- [x] `custom_song_10036.zip`: Burn My Dread
- [x] `custom_song_10037.zip`: Pursuing My True Self
- [x] `custom_song_10038.zip`: Wake Up, Get Up, Get Out There

### TeiK Charts Song Pack Vol. 1 (Normal) (14 files)
- [x] `custom_song_10002.zip`: Deep Blue
- [x] `custom_song_10070.zip`: Bokura no LIVE Kimi to no LIFE (Hasunosora Ver.) (Based on SI Show)
- [x] `custom_song_10247.zip`: Cheer Mode
- [x] `custom_song_10299.zip`: Yappa Tenshi!
- [x] `custom_song_10349.zip`: Itoshiki Yume yo Izanaite
- [x] `custom_song_10466.zip`: Like a Treasure
- [x] `custom_song_10498.zip`: Stay (MASTER: Swipe)
- [x] `custom_song_10527.zip`: Burn!!
- [x] `custom_song_10559.zip`: Circle of Love
- [x] `custom_song_10578.zip`: Yakusoku ni Nare Bokura no Uta
- [x] `custom_song_10609.zip`: Aspire
- [x] `custom_song_10614.zip`: Just woo!!
- [x] `custom_song_10638.zip`: SUNNY DAY SONG (Movie Edit FULL Ver.)
- [x] `custom_song_10639.zip`: SUNNY DAY SONG (15th Anniversary Love Live! Fest FULL Ver.)

### SIF Tournament Song Pack (9 files)

- [x] `custom_song_10624_1.zip`: Nijiiro Passions! (SIF National Tournament 2021 Exhibition Ver.)
- [x] `custom_song_10625.zip`: START!! True dreams (SIF National Tournament 2021 Exhibition Ver.)
- [x] `custom_song_10623.zip`: Fantastic Departure! (SIF National Tournament 2021 Exhibition Ver.)
- [x] `custom_song_10622_1.zip`: Yume Kataruyori Yume Utaou (SIF National Tournament 2022 Ver.)
- [x] `custom_song_10047_1.zip`: Snow Halation (SIF National Tournament Ver.)
- [x] `custom_song_10048.zip`: A song for You! You? You!! (SIF National Tournament Ver.)
- [x] `custom_song_10046.zip`: No brand girls (SIF National Tournament Ver.)
- [x] `custom_song_10045.zip`: Yuujou No Change (SIF National Tournament Ver.)
- [x] `custom_song_10044.zip`: SKY JOURNEY (SIF National Tournament Ver.)

**Coming soon (Sparklink Stars Vol. 1):** Joy in the Box, We Are aMazINC., Compass, Dance with Veil. Drop the zips into `songs/` and list them in that pack's `pack.json` when they exist.

## Troubleshooting

- **The page says it could not load `dlc.json`**: you opened it from disk. Use `python3 -m http.server` or GitHub Pages.
- **A song shows "Not uploaded yet"**: the zip is not in `songs/`, or its name differs from the one in `pack.json`.
- **"Download pack" does nothing**: the JSZip script from cdnjs was blocked. Use the per-song buttons.
- **The game says it could not read a zip**: do not unzip it, and make sure it has `manifest.json` and `audio`.
- **Pushing is rejected**: GitHub blocks single files over 100 MB. Song zips are a few MB each, so this should not happen.

## Notes

- The MyGO!!!!! and Ave Mujica zips were exported from the game's built-in data. Haruhikage is listed in the MyGO!!!!! pack as CRYCHIC.
- The full set of 87 zips is about 270 MB. GitHub recommends repos under about 1 GB, so that is fine.
- Tune Tap Simulator is an unofficial fan-made project. Songs and artwork belong to their respective owners; only host files you are allowed to share.

## Push to GitHub

```bash
git init -b main
git add .
git commit -m "DLC downloader"
git remote add origin https://github.com/<you>/tunetap-dlc-downloader.git
git push -u origin main
```
