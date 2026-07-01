# PawPal+ Project Reflection

## 1. System Design

** Core Actions **
A user should be able to add one or more pets.
A user should be able to see today's task.
A user should be able to mark complete a task the user has completed.

**a. Initial design**

- Briefly describe your initial UML design.
My initial design has 5 classes: an Owner who has many Pets and many AvailabilityWindows, each Pet requiring a list of Tasks, and a Scheduler that manages one Owner to fit tasks into available windows. Tasks carry a duration, plus Frequency and Priority enums, while AvailabilityWindows track day, time range, and capacity.
- What classes did you include, and what responsibilities did you assign to each?
owner - the main user, owns the pets and adds pets and availability
pet - owner by the main user, adds a task and stores list of tasks
task - describes what action the owner needs to complete
scheduler - looks for avaiability according to what the owner shares

**b. Design changes**

- Did your design change during implementation?
Yes, it did.
- If yes, describe at least one change and why you made it.
Added a scheduled task class that connects my Task and availability window. I made the change because I realized that for tasks to have a frequency, I needed to have multiple instances of the same task for different times in the future. Scheduled task accomplished this.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
It considers priority above everything else and then the time. It basically goes where the last task was and sees if the new task can fit. This means it's greedy by nature and isn't super smart.

- How did you decide which constraints mattered most?
I started from the smallest iteration that would be useful for a pet owner. What would an owner need to know and what would make their lives easier. An owner might prioritize tasks and care whether they fit in his schedule in general rather than strict efficiency, so I didn't make it smart.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
It doesn't schedule tasks in a smart way. If a different organization betwen tasks would let more tasks be involved, it wouldn't check it.
- Why is that tradeoff reasonable for this scenario?
This is meant as a system for one user, which may or may not have too many pets. As a first iteration to just make a pet owner's life a bit easier, it didn't seem very necessary.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used it for design and brianstorming. Then I made fixes to it's intial thoughts and once we were on the same page worked on the structure. Refactoring was easier because we already established things.
- What kinds of prompts or questions were most helpful?
Explain why this would be your first choice and ask for when it's reccoendation would backfire.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The AI implemented this to work for more than one owner, each having multiple pets and schedulers.
- How did you evaluate or verify what the AI suggested?
I first made it break down for me and I followed up with clarifying questions.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
3.8 - 4.0
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The level of detail me and the AI went to to make sure this would be auseful app for a pet owner.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
Take more control oevr the project from the AI.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
It is always better to start small and increment on it. And always commit!
