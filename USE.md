<p align="center">
    <img src="https://raw.githubusercontent.com/usnistgov/contracts/master/contracts.png"
         height="240"
         alt="Contracts logo"
         class="inline">
</p>

# Introduction

Current feature detect if a spec and a record provided match.
Run the following command to test.

    $ cnt-flower --tool sumatra.yaml --record record.zip

The command will return record.yaml file which contains the arborescence
of the record and the guessed representation type.
They are:

1. Metadata: Everything in the record should be parsable
   * and human readable by default (mimetype text)
2. Raw: Everything in the record is a binary file that
   * are not easily parsable. They will require the custom read.
3. Hybrid: Mixed content holding metadata and raw content.
