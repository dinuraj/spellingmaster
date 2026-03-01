# Manual Testing Checklist

## Setup
- [ ] App starts without errors (`python app.py`)
- [ ] Database is created at `instance/spelling.db`
- [ ] Seed data loads (`python seed_data.py`)
- [ ] Home page shows 3 word list cards

## Admin — Word List Management
- [ ] Can create a new word list
- [ ] Can edit word list name and description
- [ ] Can add a single word with hint
- [ ] Can bulk import words using the textarea
- [ ] Can delete a word (without page reload)
- [ ] Can delete an entire list
- [ ] Deleting a list also deletes its words
- [ ] Duplicate words in bulk import are silently skipped

## Quiz — Keyboard Mode
- [ ] Selecting a word list starts the quiz
- [ ] Word is spoken aloud automatically after 1 second
- [ ] "Hear Again" button replays the word
- [ ] Correct answer shows green feedback and ✅
- [ ] Wrong answer shows red feedback and the correct spelling
- [ ] Progress bar advances correctly
- [ ] "Next Word" button loads the next word
- [ ] Final word shows "See My Results" button
- [ ] Enter key submits the answer

## Quiz — Canvas Mode
- [ ] Toggle to canvas mode hides the text input
- [ ] Can draw with mouse
- [ ] Can draw with touch/stylus (on tablet)
- [ ] Clear button wipes the canvas
- [ ] Submit Writing shows the correct word for comparison
- [ ] Mark Correct / Mark Wrong buttons work correctly

## Results Page
- [ ] Score fraction displays correctly (e.g. 8/10)
- [ ] Stars display correctly (3/2/1 based on score)
- [ ] Personalised message matches the score range
- [ ] Correct words list is accurate
- [ ] Missed words list is accurate
- [ ] "Hear it" button speaks missed words
- [ ] Quiz result is saved to database
- [ ] "Try Again" starts a new quiz with the same list
- [ ] "Practice Missed Words" only quizzes on wrong words
- [ ] Confetti shows on perfect score

## Edge Cases
- [ ] Visiting `/quiz/play` with no active session redirects to home
- [ ] Empty word list shows a friendly message and no "Start Quiz" button
- [ ] 404 page shows a friendly error
- [ ] App works offline (no internet) after initial page load
