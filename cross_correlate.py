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
import pprint
import os
import collections

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("first", help="The first file to compare against in "
                                      "creating the profile.")
    #parser.add_argument("second", help="The second file to compare against in "
    #                                    "creating the profile.")
    #parser.add_argument("profile_path", help="The filepath to the profile that"
    #                                         " will be used for this"
    #                                         " correlation.")
    args = parser.parse_args()
    cc = CrossCorrelate()
    
    output = cc.process_file(args.first, 128)
    for frequency in cc.list_hashes_by_frequency(output): # Debug
        print(frequency)

class CrossCorrelate():
    """Cross correlate byte offsets between two files and adds their frequencies
        to a profile."""
    Chunk = collections.namedtuple('Chunk', ['chunk', 'hashes'])
    InputFile = collections.namedtuple('InputFile', ['name', 'type', 'chunks'])
    SubHash = collections.namedtuple('SubHash', ['subset', 'hash'])
    HashFreqSub = collections.namedtuple('HashFreqSub', ['hash', 'frequency', 'subset'])

    def gen_chunks(self, input_file, chunk_size):
        """Chunk file into blocks with size chunk_size and return a
        generator which yields them."""
        if chunk_size < 1:
            raise ValueError("Chunk size given wasn't at least one!")
        while True:
            chunk = input_file.read(chunk_size)
            if len(chunk) == 0:
                break
            yield chunk

    def gen_subsets(self, chunk):
        """Generate byte subsets from a chunk."""
        for i in range(1, len(chunk)+1):        # the current subset size
            for j in range(0, len(chunk)-i+1):  # the current subset offset
                yield chunk[j:j+i]

    def gen_chunk_hashes(self, chunk):
        """Generate a tuple of all hashes of each subset of each chunk from a 
        given chunk."""
        for subset in self.gen_subsets(chunk):
            yield self.SubHash(subset, self.fletcher_16(subset))

    def gen_file_chunks(self, file_pointer, chunk_size):
        """Process the chunks in a file into Chunk namedtuples of the following
        form:
        chunk (bytes): The chunk data.
        hashes (tuple): The hashes for each subset in the chunk.
            hash [unnamed] (int): A hash of a subset of the chunk.
        """
        chunks = self.gen_chunks(file_pointer, chunk_size)
        for chunk in chunks:
            hashes = tuple(self.gen_chunk_hashes(chunk))
            yield self.Chunk(chunk, hashes)

    def fletcher_16(self, bytes_obj):
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

    def process_file(self, filepath, chunk_size, file_type='binary'):
        """Process a file and return a namedtuple containing the following:
        name: The original name of the file before processing.
        type: The type of file it was.
        chunks: A tuple of namedtuples of the form:
            chunk (bytes): The actual chunk data.
            hashes (tuple): The hashes for each subset in the chunk along with 
            the subset.
        """
        file_pointer = open(filepath, 'rb')
        fp = file_pointer
        chunks = tuple(self.gen_file_chunks(fp, chunk_size))
        # This will just give the full filepath if we're on windows.
        return self.InputFile(fp.name.split("/")[-1], file_type, chunks) 

    def list_hashes_by_frequency(self, InputFile):
        """List the hashes from subsets of chunks in a given input file in 
        descending order with the most frequent at the top. Each hash is given
        as a three column tuple consisting of the following:
        hash: The hash of the subset.
        frequency: The number of times this hash appears in the file.
        subset: The data of the subset the hash is of.
        """
        FreqHashDict = {}
        for chunk in InputFile.chunks:
            for _hash in chunk.hashes:
                try:
                    FreqHashDict[_hash] += 1
                except KeyError:
                    FreqHashDict[_hash] = 1
        FreqHashList = []
        for _hash in FreqHashDict:
            FreqHashList.append((_hash[1], FreqHashDict[_hash], _hash[0]))
        FreqHashList.sort(key=(lambda a: a[1]))
        FreqHashList.reverse()
        for hash_frequency_subset in FreqHashList:
            yield self.HashFreqSub(hash_frequency_subset[0],
                                   hash_frequency_subset[1],
                                   hash_frequency_subset[2])

if __name__ == '__main__':
    main()
