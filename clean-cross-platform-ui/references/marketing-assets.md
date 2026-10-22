# Store screenshots, promo videos and README media

Read this when making App Store or Play Store screenshots, a promo or launch video, a README GIF, or social images.

## Contents
- Principles
- Store screenshots
- Promo video
- README media
- Checks before shipping

## Principles
- Build every frame from the app's own stylesheets and markup (load the real token and component CSS, reuse the real
  class names and copy), not from a redrawn imitation. The assets then follow the design system automatically.
- Use example data. Never show the user's real file names, folders, emails or accounts in anything that will be public.
  Numbers must add up across scenes and screenshots (selected items total the freed amount, the disk bar moves by
  that amount).
- One message per frame: a sentence-case headline (one short sentence), one supporting line in the secondary text
  color, and the product UI below it. Same palette, font and spacing as the app; no gradients, glow or device
  mockups unless asked.

## Store screenshots
- Render at the largest size the store accepts and let it scale down: macOS 2880 x 1800 (16:10; 2560 x 1600,
  1440 x 900 and 1280 x 800 are also accepted), iOS the current largest iPhone and iPad sizes. Lay out at 1x and
  capture at 2x for crisp text.
- RGB PNG with no transparency.
- Five or six screens, in this order: where the value is (what it finds or shows), how it explains itself, how it keeps
  you safe or in control, how you make it yours, the overview, and privacy or size.
- Keep the captions in a text file next to the images, and keep the store text (name, subtitle, keywords,
  description, promotional text, privacy URL) under version control within the store's character limits.
- A privacy policy is required for a listing. Describe what the app really stores and sends, nothing more.

## Promo video
- 15 to 25 seconds: hook (2 to 3 s), reveal, two or three highlights showing the product in use, outro with the mark,
  name, one line and where to get it.
- Every line on screen stays settled long enough to read (about 0.3 s per word). Pace comes from cuts and motion, not
  from pulling text away early.
- Show the product working: things appearing one by one, a cursor moving, a checkbox ticking, a dialog changing to its
  result. Dim the background before a dialog appears.
- Draw each frame as a pure function of time and capture it; place scene changes on the music's beats.
- Music and sound effects in one key, mixed softly under the visuals, about -14 LUFS for social video.
- Bake the strongest settled frame (usually the outro) into frame 0 so it becomes the thumbnail; starting on the same
  frame the video ends on makes a GIF loop cleanly.

## README media
- GitHub does not play `<video>` tags pointing at files in the repository. Use an animated GIF in the README
  (about 960px wide, 15fps, a full 256-color palette so small accents keep their color) and keep the MP4 with sound
  next to it in the assets folder.
- Put all generated media in one assets folder with plain names; no tool or workflow names in file or folder names.

## Checks before shipping
- Look at stills from every scene and from mid-transition: no overlaps, clipped text, double exposures or stray
  dividers poking past rounded corners.
- Check the final file itself (decode a frame from the encoded video or GIF), not only the source frames.
