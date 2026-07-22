# IronCorp / deecalc — a note on the brief

Ben — I've read the plan closely, and I like it. Fair warning: I haven't used deecalc, only seen it demo'd and talked it through with you, so I'm taking the engine on trust — yours is a safe pair of hands. This is about the plan and where I'd aim it, not the build.

Start with something from my own valuation work this week. The same DCF came out at $3.48 a share three different ways, each set of inputs tidy in itself — and a scope error I nearly missed, leaving a business that's being sold inside forecast sales, would have given a clean, exact, re-runnable answer that was simply on the wrong basis.

The lesson isn't "wrong inputs, wrong answers" — everyone knows that, and I wouldn't claim Excel would have caught it either; every model carries a mistake you haven't found yet. The narrower point is that being exact and re-runnable does nothing for the thing that matters most: finding the error before it ships. Re-running just reproduces it, confidently.

That's where I'd put the real pitch. deecalc is unusually well-placed to help *find* that error — better than Excel — if it's built for it. That's worth more than the exact-and-repeatable part.

## Why deecalc could make the error easier to find

1. **It shows what the answer hangs on.** It can point straight at the few inputs that actually drive the number — where an error does damage, and where you look first. Excel needs hours of data tables to say the same thing. (As the headline valuation output the feature is weaker — a local slope, when most of the value sits years out — but for finding where to look it's exactly right.)

2. **It can work backwards.** "What would this input have to be to match the market price?" exposes an assumption that's fine alone but absurd in company — an implied margin above the industry's best-ever. Excel's version is a throwaway goal-seek.

3. **It can mark the soft inputs.** Flag the shaky ones — wide error band, contested method — so scrutiny goes there first.

4. **It makes a number traceable — to its source, and to what changed.** Drill down to where a number is made in a click; and because two versions differ in a listed way, "the value moved forty cents since Monday — which input did that?" is answerable. Most errors arrive with a change.

5. **It can object when the story doesn't hang together.** If it checks the economics are coherent, not just that the accounts balance, a class of mistakes becomes something the model refuses, rather than something a reviewer has to notice.

None of these is automatic; each is a choice to build for finding mistakes. That's the differentiator, and it holds for any model — a loan, a buyout, a budget — not just a valuation.

## Focus

Back the engine and deecalc, then be stricter than the brief about who it's for. The plan tries to do a lot before deciding the first market; I'd decide that first and let it prune the rest.

A full accounting system is the biggest bet and, on the brief's own admission, only wins the smallest clients — I'd park it, keeping just a simple way to bring in accounts when a valuation needs them. Prove the tool on one real, messy company rather than a tidy fixture: the mess — a business being sold, one-offs, foreign currency — is the hard part, and where trust is earned. The agent-queryable model is a good idea worth a cheap decision now — build the app to ask the model through a clean doorway — and the machinery later.

## One thing it must do

People have to be able to take their work into Excel to share it. That only clashes with the re-run guarantee if export is an afterthought — make it a proper snapshot, with the live model still the real one.

## What I'd do

Pick the first market. Spend the effort on making the tool good at catching the error — the five things above — because that's what nothing else does. Prove it on one real company, end to end. Keep accounting and the ask-the-model feature as options, not promises.

Good work, and I want to build on it. This is only about where the hard part is. Tell me where you see it differently.
