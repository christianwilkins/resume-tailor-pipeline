# ai-powered resume tailoring system

automatically tailor your latex resume for specific job postings using ai. track versions and get pdfs through github releases.

## how to use

### step 1: fork repo
you need to fork this repo to get releases with a generated pdf like i am. this will greatly help you keep track of your applications and different versions.

### step 2: clone repo + ide setup
clone the repo. you NEED an agentic code editor extension for vsc. i suggest copilot with github pro (free for students). but feel free to use cline, or another extension. you can also use ai ides like cursor or windsurf. anything that allows llms to read files, do online research and write latex.

### step 3: file setup
fill `master-resume.tex` with your resume in latex (currently filled with my resume). you can even include more than a page, if you have that much experience. the llm will pick the most important ones based on the position for you.

fill `job-posting.txt` with the posting you want to apply for.

### step 4: running it
just open your ai agent extension and tell it to follow the edit prompt. the output will be in `resume.tex`.

you will need to check if it fills up a page or not. i would suggest installing a latex pdf builder in your ide; e.g. mactex for macos; etc... or you can just use overleaf in web app.

if the output is too little, too much, or some of it is a hallucinating; ask the llm or fix it yourself. this should give you either a resume that you can apply out of the gate with; or something that is a great start for tailoring a position you want.

### step 5: git add, commit, and push
when you push your new resume (in the `resume.tex` file); github actions will automatically create a pdf for it in the release tab AND name the release based on the commit message.

because of this, you should name your commits the company you are applying for e.g. "meta new grad 2025" and so on... will help you keep track
