# repo-folder-to-single-text-for-gpt-prompt

`repo-folder-to-single-text-for-gpt-prompt` is a command-line tool that converts the contents of a Git repository into a text format, preserving the structure of the files and file contents. The generated output can be interpreted by AI language models, allowing them to process the repository's contents for various tasks, such as code review or documentation generation.

## Getting Started

To get started with `repo-folder-to-single-text-for-gpt-prompt`, follow these steps:

1. Ensure you have Python 3 installed on your system.
2. Clone or download the `repo-folder-to-single-text-for-gpt-prompt` repository.
3. Navigate to the repository's root directory in your terminal.
4. Run `repo-folder-to-single-text-for-gpt-prompt` with the following command:

   ```bash
   python repo_folder_to_single_text.py /path/to/git/repository [-f /path/to/folder/containing/git/repos] [-p /path/to/preamble.txt] [-o /path/to/output_file.txt]
   ```
    Replace `/path/to/git/repository` with the path to the Git repository you want to process. 
    Optionally you can add a -f tag to recursively process all folders in the provided path and generate output within the main folder path itself with the repo name. Optionally, you can specify a preamble file with -p or an output file with -o. If not specified, the default output file will be named output.txt in the current directory.

5. The tool will generate an output.txt file containing the text representation of the repository or the ouptput files will be recusrsively added to provided folder path with -f flag. You can now use this file as input for AI language models or other text-based processing tasks.

## Running Tests

To run the tests for `repo-folder-to-single-text-for-gpt-prompt`, follow these steps:

1. Ensure you have Python 3 installed on your system.
2. Navigate to the repository's root directory in your terminal.
3. Run the tests with the following command:

   ```bash
   python -m unittest test_repo_folder_to_single_text.py
   ```
Now, the test harness is added to the `repo-folder-to-single-text-for-gpt-prompt` project. You can run the tests by executing the command `python -m unittest test_repo_folder_to_single_text.py` in your terminal.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
