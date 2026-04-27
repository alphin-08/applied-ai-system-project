# PawPal+ Reflection — After Implementing AI

---

## 1. Limitations and Biases in the System

**The database is hand-written and static**
Every rule in the code was written by a person so it only knows what that person knows. If the creator did not know much about certain pets or health conditions then those blind spots get passed straight to the AI. For example, the current database is great for dogs and cats but has almost nothing for other pets. A rabbit owner would just get generic animal advice instead of facts meant specifically for their actual pet.

**The health keyword search is very basic**
The app searches for exact words like joint or kidney in the health notes. If an owner types bad knees instead of joint issues, the app will not find the right health rules and the AI will never see them. The system just looks for exact matches and does not understand synonyms or complex medical words at all.

**The AI has no memory between sessions**
Every time you build a schedule, the AI starts completely from scratch with no idea what happened on previous days. It cannot notice patterns like a dog missing its walk three days in a row because it never saves any of your history.

**The AI can still hallucinate**
The AI can still make things up sometimes. Even though the code tells Gemini to only use the facts from the database, there is no real way to force it to listen. The AI can and sometimes will add advice that was never in the code to begin with. There is no extra tool to fact check the AI before the user sees the final summary.

---

## 2. Could the System Be Misused?

The biggest risk is that an owner might use the AI advice instead of going to a real vet. The summaries sound very confident and use real care rules. It is easy to see someone reading a detailed paragraph about their sick cat and deciding not to call the vet. This is dangerous because the system is not a doctor. It does not know the specific history of the animal and it cannot physically examine the pet.

**How I prevent this right now**
The code specifically tells the AI to act like a care helper and never like a real veterinarian. The AI summaries also constantly remind the user to talk to a vet before making any big medical decisions. I also made sure the owner has to manually click a button to mark tasks as done. This keeps the human in control instead of letting the AI run everything on its own.

**What I could add in the future**
I could add a permanent warning banner on the website that tells people the AI does not replace professional veterinary care. I could also build a filter that scans the AI output before the user sees it. If the AI tries to give specific medicine doses or treatment advice, the filter would catch it and tell the user to verify the information with a real doctor.

---

## 3. What Surprised Me While Testing Reliability

The biggest surprise was how much the AI relied on the search tool instead of the AI model itself. During my tests, the AI gave the best advice when the search tool found four or five specific facts about the pet. When the search tool only found a few facts about a healthy pet, the final summary was much shorter and sounded very generic. I originally thought the AI model would be the hardest part to get right. In reality, the AI was always good and the real challenge was making sure the search tool gave it the best information. If you give the AI basic facts, it will just give you basic advice.

My second big surprise was how the free Gemini API actually works. Every AI model I tried gave me an error that said my free limit was zero. The problem was not the model I picked but the Google Cloud account my key was connected to. If your project has billing turned on at all, you lose access to the free tier completely. This rule was not explained clearly anywhere and it wasted a lot of my time before I finally figured out the actual problem.

---

## 4. Collaboration with AI During This Project

I used Claude AI as an assistant for a lot of this project, but I was the one doing the actual planning and building. It helped me with the first classes at the beginning, and it assisted with the final AI tools at the end.

**One time the AI gave a helpful suggestion:**
When the Gemini API kept returning a quota error that said my free limit was zero, I assumed the problem was the model name and kept switching models. The AI pointed out that the real issue was not the model at all, it was the Google Cloud project my API key was attached to. Any project that has ever had billing enabled loses free tier access completely, regardless of which model you use. That diagnosis was non-obvious and saved a lot of time because I would have kept switching models without ever finding the root cause.

**One time the AI gave a bad suggestion:**
When I first asked the AI to remove duplicate pets from the schedule, it wrote a standard line of Python code to create a set. I ran it and the program immediately crashed with an unhashable type error. The code the AI wrote looked perfectly fine, but it forgot that Python data classes cannot be hashed by default. I had to find the real problem and replace the set with a dictionary that used the pet name instead. This was a great example of why you always need to read and understand AI code before you use it because it can make hidden assumptions about your project.
