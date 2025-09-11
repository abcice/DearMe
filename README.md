# DearMe

## 📖 Future Diary / Time Capsule App  

## 🎯 Core Concept  
A **Future Diary app** that allows users to:  
- Store letters, daily diary entries, media, and personal favorites for themselves or loved ones.  
- Unlock memories only at specific times in the future (like a time capsule).  
- Keep a **private encrypted diary** safe from everyone, even developers.  
- Share or co-create memories with trusted people.  
- Preserve legacy through posthumous letters.  
- Experience unique flashbacks and analytics on their life journey.  

---

## 📝 Core Features  

### 1. Letters & Messages  
- Write letters to yourself or others.  
- Choose a future unlock date (stays hidden until then).  
- “Surprise me” unlock date (random 2–10 years).  

### 2. Media Support  
- Upload and attach photos, videos, voice letters, PDFs.  
- Store achievements, milestones, or life events.  

### 3. Daily Diary (Encrypted)  
- Write daily encrypted diary entries.  
- Even developers cannot read diary entries.  
- Diary entries can include:  
  - Free-form text.  
  - Favorite music (with optional uploaded MP3).  
  - Favorite foods (text).  
  - Favorite anime/TV shows (text + optional links).  

### 4. Tagging & Categorization  
- Add tags (funny, emotional, travel, achievement, family, etc.).  
- Custom tags.  
- Filter/search memories by tags.  

### 5. Timeline & Albums  
- Chronological view of memories.  
- Albums with thumbnails.  
- Travel log: attach country/location → displayed on a map.  
- Shared timelines for couples, families, or friends.  

### 6. Random Flashbacks  
- On login, show a random unlocked memory.  
- “I’m sad” button → happy/motivational memories.  

### 7. Anniversaries  
- Old letters/photos re-unlock on anniversaries (5, 10+ years).  
- Example: “Your graduation letter, 10 years later.”  

### 8. Social & Joined Memories  
- Friend system (send/accept requests).  
- Share memories via app, email, or SMS.  
- **Joined memories**: couples/friends co-create memories (wedding anniversary, trips, etc.).  
- Shared albums/timelines.  

### 9. Notifications & Reminders  
- In-app notifications for unlock events.  
- Email reminders (important if app is deleted).  
- Optional SMS notifications.  

### 10. Privacy & Security  
- Visibility: private, friends-only, public.  
- End-to-end encryption for diary entries.  
- “Grave memories” → private forever, never shared.  

### 11. Posthumous Memories (Legacy Handover)  
- Assign trusted contacts.  
- After user’s passing, scheduled letters delivered.  
- Example: final goodbye or advice letters.  

---

## 🌟 Advanced & Unique Features  

1. **Voice Letters** – record and store audio securely.  
2. **AR Flashbacks (Future Idea)** – overlay old photos in current locations.  
3. **Memory Bundles** – export as PDF “memory books.”  
4. **Sentimental Analytics** – mood tracking, word clouds, memory types.  
5. **Gamification** – badges for writing regularly, uploading media, journaling streaks.  

---

## 📊 Example Use Cases  

1. Write a letter to your future self to open in 5 years.  
2. Keep an encrypted daily diary no one else can ever read.  
3. Leave a travel diary with photos + locations to relive trips.  
4. Revisit your favorite anime/music list from years ago.  
5. Random surprise unlock → system picks one memory.  
6. Click “I’m sad” → see uplifting memories.  
7. Spouse/children receive legacy letters after death.  
8. Visit your childhood home → see AR flashback.  
9. A couple co-creates a shared anniversary capsule.  

---

## 📂 Data Structure (Database Plan)  

### User  
- `id`  
- `username`  
- `email`  
- `password` (hashed)  
- `profile_pic`  
- `bio`  

### DiaryEntry (Encrypted)  
- `id`  
- `user_id (FK)`  
- `date`  
- `encrypted_content`  
- `favorite_music` (file or link)  
- `favorite_food` (text)  
- `favorite_anime_tv` (text + link)  

### Memory  
- `id`  
- `user_id (FK)`  
- `title`  
- `content` (encrypted text)  
- `unlock_date`  
- `surprise_unlock` (boolean)  
- `visibility` (private/friends/public)  
- `location` (optional)  
- `tags` (many-to-many)  

### Media  
- `id`  
- `memory_id (FK)`  
- `file_type` (photo/video/audio/pdf)  
- `file_path`  

### JoinedMemory  
- `id`  
- `title`  
- `unlock_date`  
- `participants` (many-to-many User)  

### LegacyContact  
- `id`  
- `user_id (FK)`  
- `contact_user_id (FK)`  
- `relationship` (spouse, child, friend)  

### Notifications  
- `id`  
- `user_id (FK)`  
- `type` (unlock, anniversary, reminder)  
- `status` (sent/pending)  

---

## 👤 User Stories  

- As a user, I want to write a letter and set a date so that my future self can receive it.  
- As a user, I want to write a private encrypted diary entry so that no one, not even developers, can read it.  
- As a user, I want to upload my favorite music, foods, and shows so that I can look back at my changing tastes.  
- As a user, I want to attach photos, videos, or voice letters to my memories so that they feel more alive.  
- As a user, I want to tag my memories so that I can easily find them later.  
- As a user, I want to see my memories on a timeline or map so that I can revisit my life story.  
- As a user, I want the app to remind me of anniversaries so I can relive old moments.  
- As a user, I want to create joined memories with my partner so we can unlock them together in the future.  
- As a user, I want to assign legacy contacts so that my memories can reach loved ones if I pass away.  
- As a user, I want random flashbacks so that I get surprise doses of nostalgia.  
- As a user, I want to export my memories as a PDF book so I can keep them offline.  

---

## ⚙️ Tech Stack  

- **Backend:** Django + PostgreSQL (or SQLite for local dev).  
- **Frontend:** Django templates (or optional React).  
- **Authentication:** Django built-in sessions.  
- **Storage:** Django file storage (images, audio, video, PDFs).  
- **Scheduling:** Celery + Redis for delayed unlocks.  
- **Encryption:** Django cryptography for diary entries.  
- **API (optional):** Django REST Framework.  

---

## 🚀 Next Steps (Stretch Goals)  

- AI-powered “memory insights” (detect sentiment in diary entries).  
- Cloud storage integration (AWS S3, GCP).  
- Mobile app version.  
- AR flashbacks fully implemented.  

---

## 📸 Screenshot / Logo  
*(To be added after first prototype is built)*  

---

## 🙌 Attributions  
- Django, Celery, Redis, DRF.  
- Any external libraries or assets used will be listed here.  

---

[wireFrame](https://excalidraw.com/#json=eVwD55XHqNuyxwoT7YneB,JFn3m1v8vgdO_t69H1gQgQ)

[trello](https://trello.com/invite/b/68c2b808f32436b85099c94e/ATTI33b6548ef1fd1e644dab4ab32d0af29f8C05B60E/dearme)

[ERD](https://drive.google.com/file/d/1Hx5I5N8FdV6dChbVy_Uwsc6oURAQ7Z3K/view?usp=sharing)