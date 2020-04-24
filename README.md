# Picture-Perfect
Picture Perfect is an image management application built in Python version 2.7. Uses the Tkinter package and PIL (python imaging library). Picture Perfect was made for Hoffmann & Fiege Consulting Engineers. All requirements were obtained directly from H&F employees. This application's intended use is for creating technical reports that display pictures taken from on-site evaluations.

# Instructions
1. Open the directory containing the images to be used.
2. Once opened, all images can be seen on a preview screen. The user may interact with the images in the preview screen.
   * Rename all pictures at once or individually.
   * Rotate and crop images.
   * Preview an image in full screen.
3. When the user is satisfied with all images, they may edit the layout of the document.
   * Edit the ordering of images and exclude specific images.
   * Add a border around each image.
   * Add an optional label below each image and choose what information is included, such as image name, date created, and a user entered comment.
   * Add an optional header or footer and choose what information to include in each, such as directory name, date/time, page number.
   * Define the images layout by doing either one or both of the following:
         1. Defining the grid size, in columns and rows, for how to display images on each page. This will alert the user that images will automatically resize to try to fit into the grid.
         2. Defining how many pages the document should be. This also alerts the user that images will be automatically resized. Page count is limited by how many pictures the user has included in the document.
4. Finally the user can either save a pdf document to a specified directory on their computer or print the pdf to a printer on their network.



