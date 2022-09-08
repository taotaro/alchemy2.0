# alchemy2.0

Stable version of alchemy. Libraries are implemented. No Jupyter notebooks are allowed here. When your functions are ready, you can move it to this repo.

```main``` - Our production branch. If you are not sure your code will work, don't push it here. This must be the most stable.

## Things to keep in mind:
1. Please create a branch from ```main``` to make any fixes. Name your branch ```{fix_name}/{your_name}```. E.g., if the fix is to create a new scraper library, it will be ```scrape/tamara```
2. When working on your own feature branch, do not forget to periodically update your local branch with the release branch to reduce likelikehood/size of merge conflicts
    - Instead of ```git pull``` we use ```git pull --rebase``` to pull changes from remote branch to our local branch. Rebasing helps to keep our Gitflow neat and linear which makes it easy to keep track of and trace
    - How to update your branch with latest code from ```main```:
      ```
      git pull --rebase origin main
      ```
    - Then push the changes to origin to keep the history of your branch intact:
      ```
      git push --force
      ```
    - Install the most updated packages from ```requirements.txt```:
      ```
      pip3 install -r requirements.txt
      ```
3. When all code changes have been finished in your feature branch, create a Pull Request and your peers review it before merging.
4. Update the ```requirements.txt``` if there are any new modules you installed. How to update: 
    ```
    pip3 freeze > requirements.txt
    ```
