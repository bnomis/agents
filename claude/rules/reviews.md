# Reviews

When the user has to review something - snapshot or output diffs, a spec,
measurement results, generated data, a decision - hand it to them as a review
document, not as commands to run or raw diffs to read in the terminal.

## The review document

Write it as a file in the repo (for example next to the task list that asks
for the review), so it stays as the record. In this order:

1. **What is being reviewed and how**: one paragraph - what changed, why, and
   what the user does with each item.
2. **Automatic checks**: every check a script can make, run before the user
   sees anything, each shown as pass or fail with the offending items.
3. **The items**: each change with a short commentary on its cause, and what
   it is in plain words, not only its identifier. Changes with no explanation
   go in their own list, marked as needing attention.
4. **Decisions**: each decision needed, with concrete options and a
   recommendation where there is one, explained as below.
5. **Answers**: left empty for the user's verdict, filled in afterwards with
   the date.

Raw diffs are for seeing a change in context, not the way in.

## Explain every decision

A decision must stand on its own for a reader who has not followed the work
that led to it. Give each one:

- **What is being decided**, in one sentence.
- **Background**: the behaviour or history it depends on, in plain words,
  with dates.
- **What it affects**: files, run time, coverage, follow-on work.
- **Each option**: what happens next if it is chosen, not only its label.

A decision that names an option without its consequences cannot be answered
without asking.

- **Find why a setting has its value before recommending a change to it.**
  Search the project's specs, measurements, reviews and `TODO.md` for the
  setting's name, and put the reason it was chosen, with its date, in the
  background. Where a measurement tool and gold data exist, measure; a
  handful of probe examples is not a basis for a recommendation.
- **Only call something a decision when the user has something to choose.**
  A choice already made is reported as one ("I chose X because Y; it is
  reversible"), not presented as a decision.

## Make it interactive

Where possible, also publish the review as an interactive web page (an
Artifact), and read the user's answers back from it. Copy the answers into the
document's Answers section.

- **Each decision stands on the page**: its background, what it affects, why
  the recommended option is recommended, and each option's consequence, as
  above - not a link back to the document.
- **Answers are clicks**: approve or flag each item, pick an option for each
  decision, with a comment box beside each.
- **One click accepts the recommendations**: a button at the top picks the
  recommended option for every decision and approves every item, saving
  each answer as if clicked by hand. It fills only what is still
  unanswered, so a flag or a different option already chosen stays, and
  every answer can still be changed afterwards.
- **Every answer saves as it is made**, to storage Claude can read back (the
  artifact's shared database, not the browser's). No save button and no
  final submit: the user should never have to click save, let alone more
  than once.

Before publishing a review page:

- read this rule from disk again, not from a copy loaded earlier in the
  session: it changes while sessions run, and a page built from an older
  copy misses what was added since;
- check that no button exists only to save: a click on an option writes at
  once, and a comment writes after a pause in typing and when its box loses
  focus;
- check that the accept-all button saves an answer for every unanswered
  item and decision, and leaves answers already given unchanged;
- if its script was copied from another page, copy it by a marker, not by
  line number, run `node --check` on it, and render it once against a stub
  DOM to confirm every item and decision appears.

## Handing it over

- Give the page's URL in the message and open it, and name the same URL in
  the review document's header, so either leads to the other.
- When the user has documents to read or approve - specs, reviews, amended
  specs - list each one with its full absolute path, one per line, amended
  ones included, and offer to publish them as a page.

## When planning work

A spec or task list with a human review step names the review document's
path and contents, and says that the work stops until every item has an
answer.

## Related

- [markdown.md](markdown.md) - formatting conventions for the document
