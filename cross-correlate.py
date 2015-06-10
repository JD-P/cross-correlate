"""
Copyright (c) 2015, John David Pressman
    All rights reserved.
     
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
   * Neither the name of the <organization> nor the
     names of its contributors may be used to endorse or promote products
     derived from this software without specific prior written permission.
     
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
     
import argparse
import json
import os

def main():
    parser = arpgarse.ArgumentParser()
    parser.add_argument("first", help="The first file to compare against in "
                                      "creating the profile.")
    parser.add_argument("second", help="The second file to compare against in "
                                        "creating the profile.")
    parser.add_argument("profile_path", help="The filepath to the profile that"
                                             " will be used for this"
                                             " correlation.")
    arguments = parser.parse_args()

class CrossCorrelate():
    """Cross correlate byte offsets between two files and adds their frequencies
        to a profile."""
    def chunk_file(file, chunk_size):
        """Chunk file into blocks according to chunk_size and return chunks as
        list."""
        chunks = []
        chunk = None
        while chunk != 'EOF':
            chunk = file.read(chunk_size)
            chunks.append({"chunk":chunk})
        return chunks

    def generate_subsets(chunks):
        """Generate byte subsets from a list of chunk dicts."""
        for chunk in chunks:
            chunk_bytes = chunks[chunk]

    def fletcher_16(bytes_obj):
        """Compute a fletcher 16 bit checksum with modular arithmetic."""
        simple = 255
        fletcher = 255
        for byte in bytes_obj:
            simple += byte
            fletcher += simple
        simple = (simple & 255) + (simple >> 8)
        fletcher = (fletcher & 255) + (fletcher >> 8)
        simple = (simple & 255) + (simple >> 8)
        fletcher = (fletcher & 255) + (fletcher >> 8)
        return fletcher << 8 | simple


