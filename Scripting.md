This is a test for python's git pull

# TeaseAI Scripting Documentation

One of my goals for this project was to simplify the scripting language of the original TeaseAI and make it more accessible for non-programmer types.  However, the richness of functionality that makes TeaseAI really interesting necessitates a certain level of complexity.  As I have been unable to do much to reduce this complexity within the syntax of the scripting language itself, it is my hope that producing exhuastive and comprehensive documentation will be enough to diminish the barrier of entry into TeaseAI scripting.

## Introduction - Your First Script

While scripts can vary greatly in function, they all take the same basic form.  A script is made up of a handful of different types of statements that get interpreted by the program to carry out various different objectives.  These statements (or "tokens" as they're called in computer lexicology) will fall into one of the following basic categories:

1. A decorator token
2. A dialog token
3. A vocabulary token
4. A function token
5. An answer token
6. An anchor token
   
We will go through the different types of tokens, their usage and their purpose in the general order that you will encounter them within a TeaseAI script.  All TeaseAI scripts begin with the following "boilerplate" structure.

```
@Info Description of your script goes here

end()
```

The first line that begins with `@Info` is a decorator token.  Decorator tokens always begin with `@` and simply set apart lines of code that are used behind the scenes by TeaseAI to accomplish various things.  The `@Info` decorator is required by every script, and must be the first line.  It simply passes the software a description of what the script we're writing is going to do.  The software uses this information to populate the description box in the user interface that shows the user all of their installed scripts.  The software will grab all the text that follows the `@Info` decorator until it reaches an invisible "newline character" that gets inserted into any text document when you push enter.  Simply fill in as much info as you want in your description and push enter.  If you want to leave a blank line after the `@Info` decorator, you may do so.  The parser will take care of stripping blank lines out of the script at runtime, so you can feel free to use blank lines to seperate chunks of your script from one another if this helps you stay organized as you go.

The other line in our "boilerplate" code is the `end()` line.  `end()` is actually a function.  We'll cover functions later.   All you need to know about it for right now is that you must end your script with `end()` on a line by itself.

Having populated our `@Info` line with a meaningful description, and making sure we have our `end()` in place, we're now ready to start making our script actually do things.  The most common type of token you will use in your TeaseAI scripts is a dialog token, and its also the simplest to use.   A dialog token simply lays out a line of dialog that our AI domme will "speak" into the chat window.  We don't need any sort of special syntax for dialog; simply type what you want the domme to say, and press enter.   Let's start with the traditional "Hello, world" script.

```
@Info The domme announces her presence to the world.

Hello, world!

end()
```

If we were to run this script in the program, we would see a line of dialog get pushed to the chat window by our domme, announcing, "Hello, world!" before the script reaches the `end()` function and simply exits.  We won't see any output from the `@Info` decorator or the `end()` function.  These are commands that carry out "behind the scenes" functionality.   If you've followed along to this point, you've technically completed your first script!  It's not the most interesting script, but it loads, executes some commands and then exits, so mission accomplished!  

Of course, you're probably hoping to do something a bit more clever than merely saying hello, so let's make use of another type of token and make our script do something a little more exciting.  We're going to use one of TeaseAI's many *vocabulary* tokens to introduce some variability into the language of our introduction, so it doesn't say the same thing every single time.  Vocabulary tokens are also very simple to use.  We simply surround one of TeaseAI's many included vocabulary words with underscores.   Hello is one such word, so let's change our script to read:

```
@Info The domme announces her presence to the world.

_Hello_, world!

end()
```

Simple, right?  Now, when the script runs, when the parser reaches the `_Hello_` vocabulary token, it will randomly substitute one of a number of synonyms in its place.  So the output might look something like one of the following:

```
Domme: Greetings, world!
Domme: Hi, world!
Domme: Heya, world!
```

Now our domme isn't quite so boring!  Instead of just repeating the same line every time the script runs, we can get different output.  TeaseAI has a large number of these vocabulary words built in for you.   You will find them all listed in one of the appendices of the documentation.  If you did any scripting on previous versions of TeaseAI, you'll notice there are no more vocabulary flat files to manage, and no more broken scripts when they're not in place or not formatted properly.  Vocabulary is now handled behind the scenes in a database.  One of the many advantages that this method has over the previous approach of using flat files is that the vocabulary relationship is now "many to many" instead of "one to many."  What this means is that the vocabulary token will work exactly the same if you use `_Hello_` or if you use `_Greetings_` or `_Hi_`, or any of the other synonyms of 'Hello' currently supported by the database.

To really begin to explore what TeaseAI can do, we need to introduce another token.  We want to be able to have our domme make some decisions about how she's going to proceed to interact with us, and personalize the experience along the way.  To accomplish this, our script needs to be able to execute some logic.  This is where the function category of tokens comes into play.   

There are a number of functions built into TeaseAI for carrying out various tasks.  All functions utilize the same syntax.  You call a function by its name and following the call to a function name, you must always include a set of parentheses `()`.  Some functions have parameters (also known as "arguments") through which we can pass the function the information it requires to carry out the logic we need, and that's what goes in the parentheses.  In the case that we need to pass the function more than one argument, we simply separate them with commas.  Arguments must be passed in the proper order.  The documentation lists every available function, and lists any required arguments in the order that you need to pass them to the function.  It's important to note that the parentheses are required whether you are passing an argument to a function or not!  In this case, we're going to use the `var()` function to get the user's name from the program options.  `var()` simply returns the value of one of the program's many variables.  It requires one argument, the name of the variable we want to return, which in this case is 'chat_name'.   So we can personalize our greeting by doing something like this:


```
@Info The domme greets the user by name.

_Hello_, var(chat_name)!

end()
```

Now when we run our script, our output might look like one of:

```
Domme: Greetings, Michael!
Domme: Hi, Michael!
Domme: Heya, Michael!
```

This assumes, of course, that the user has set their name in the program options to 'Michael.'  The `var(chat_name)` call will return whatever the user has entered into the 'Chat Name' field in the options menu, so simply plug it into your script where you want the user's name to appear, and the parser takes care of the rest!

Now let's have our domme ask the user a question and do something different based on the user's response.  We're going to have to use a couple of functions to accomplish this, and in so doing, we'll learn about the last two categories of tokens in TeaseAI scripts, _answers_ and _anchors_.  Modify your script so it looks like this:

```
@Info The domme greets the user by name and wants to know if they're happy to see her.

_Hello_, var(chat_name)!
Are you as happy to see me as I am to see you?  
answer(10, Are you happy to see me or not? _*grins*_)  

end()
```

Do you see the new function call?  We're now calling the `answer()` function, which will receive some input from the user, and our program will then follow a different branch of logic depending on how the user answers the question.  You may have noticed that the answer function requires two arguments.  The first argument is a number of seconds to wait without receiving valid input from the user before prompting them again to answer our question.  The number must be an integer (meaning a whole number including no decimals or fractions).  The second argument is a line of dialog to send if the user hasn't answered our question within the amount of time we set through the first argument.   In this case, `answer(10, Are you happy to see me or not? _*grins*_)` means that our script will wait 10 seconds at this point, and if we haven't received a valid response by that time, we'll prompt the user again by having the domme say "Are you happy to see me or not? \*grins\*"  `_*grins*_` is, of course, a vocabulary token, and will be replaced by one of a number of different synonyms to punctuate our question.   

So now that we understand the function call, how do we tell the program what kind of input should be considered valid?  The _answer_ token!  When we're expecting input from the user, we need to tell the program what sort of answers we expect, and how to handle them if we get them.  We'll handle a simple yes or no here, but in practice, you probably want to try to anticipate a few others ways a user might choose to respond to this question, so you can have the domme respond appropriately if they're trying to be a pain in the ass!

The syntax for answer tokens is as follows:  Put each answer you want to handle on a newline beginning with a hyphen `-`.   Follow the hyphen with a space, and then enclose the response you want to handle in a set of double asterisks `**`.  It should look something like this:

```
@Info The domme greets the user by name and wants to know if they're happy to see her.

_Hello_, var(chat_name)!
Are you as happy to see me as I am to see you?  
answer(10, Are you happy to see me or not? _*grins*_)  
- **no** No? goto(You Must Know What I'm About To Do)  
- **yes** I'm glad to hear that var(chat_name)  

end()
```

Now the program will compare the input from the user to the responses we have attached logic to.  If the user input matches up with one of the responses we've laid out, the program will execute the remainder of the code on that line, whatever it may include.  Instead of a single word answer, you may provide a comma separated list of answers that will satisfy that condition.  So we could have written this logic like this:

```
@Info The domme greets the user by name and wants to know if they're happy to see her.

_Hello_, var(chat_name)!
Are you as happy to see me as I am to see you?  
answer(10, Are you happy to see me or not? _*grins*_)  
- **no, nope** No? goto(You Must Know What I'm About To Do)  
- **yes, yeah, ya, yea, yah, yup** I'm glad to hear that var(chat_name)  

end()
```
However, the program will parse any words within an answer token that represent a vocabulary token and automatically "understand" any of the synonyms of "No" that it's aware of to satisfy the `- **no**` condition.   Pretty neat, huh?   

You may also handle as many responses as you care to for a given call to `answer()`.  You're not limited to just two!  However, be aware that `answer()` is _recursive_ which means it will infinitely loop until its condition for advancing is satisfied, so if your question is overly complex and your response handling overly specific, you run the risk of leaving the user in a state of being "stuck," unable to advance the script for lack of being able to discern an appropriate response.  It's best to always have at least one fairly obvious response to avoid this.

If you were paying attention, you probably noticed another new function call in the last example.  Attached to the "no" response is a `goto()` statement.  A `goto()` call simply skips ahead to another part of the script.  Finally, our last token category!  The _anchor_ token.  When you call `goto()`, you must pass it an anchor as an argument.  The anchor itself must come _after_ the `goto()` call.  The syntax for an anchor is simply a line of text that starts with a `#` followed by a space.   What follows is the name of the anchor.   You're free to assign any name you want.   You can choose to simply use numbers, or something more descriptive, like what's been demonstrated here.   The `goto()` call will advance to the anchor that matches the argument you pass to it, and skip over any code between the current position in the script and pick up execution with the line immediately following the anchor.   Let's put in the anchor for our `goto()` and finish out this portion of the script!

```
@Info The domme greets the user by name and wants to know if they're happy to see her.

_Hello_, var(chat_name)!
Are you as happy to see me as I am to see you?  
answer(10, Are you happy to see me or not? _*grins*_)  
- **no** No? goto(You Must Know What I'm About To Do)  
- **yes** I'm glad to hear that var(chat_name)  

I've been thinking about all these fun ways to torment a _cock_  
And there's not a lot of guys who can handle that  
That's why I'm always glad to see you here willing to please me  
And willing to suffer _*grins*_  
Speaking of suffering...  
goto(Start Stroking)  

# You Must Know What I'm About To Do
You must know what I'm about to do to that _cock_ then _*grins*_  
But since you knew and logged on anyway  
I don't have to feel guilty about it *lol*  

# Start Stroking
startStroking()
end()
```
