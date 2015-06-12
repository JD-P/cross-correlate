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
    for frequency in cc.list_hashes_by_frequency(output.frequencies): # Debug
        print(frequency)

class CrossCorrelate():
    """Cross correlate byte offsets between two files and adds their frequencies
        to a profile."""
    Chunk = collections.namedtuple('Chunk', ['chunk', 'subset_slices'])
    InputFile = collections.namedtuple('InputFile', ['name', 'type', 'frequencies', 'chunks'])
    HashSlice = collections.namedtuple('SubHash', ['hash', 'start', 'end'])
    SubSlice = collections.namedtuple('SubSlice', ['start', 'end'])
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

    def gen_slices(self, chunk):
        """Generate byte subsets from a chunk."""
        for i in range(1, len(chunk)+1):        # the current subset size
            for j in range(0, len(chunk)-i+1):  # the current subset offset
                yield self.SubSlice(j, j+i)

    def gen_chunk_hashes(self, chunk):
        """Generate all hashes of each subset of a given chunk."""
        for _slice in self.gen_slices(chunk):
            subset = chunk[_slice[0]:_slice[1]]
            yield self.HashSlice(self.fletcher_16(subset), _slice[0], _slice[1])

    def gen_file_chunks(self, file_pointer, chunk_size):
        """Process the chunks in a file into Chunk namedtuples of the following
        form:
        chunk (bytes): The chunk data.
        subset_slices (tuple): A tuple containing named tuples that tell where
        to slice to generate subsets:
            start: The start of the slice.
            end: The end of the slice.
        """
        chunks = self.gen_chunks(file_pointer, chunk_size)
        for chunk in chunks:
            subsets = tuple(self.gen_slices(chunk))
            yield self.Chunk(chunk, subsets)

    def create_hash_table(self, file_pointer, chunk_size):
        """Create a hash dict containing the frequencies of fletcher hashes of
        subsets between chunks in the file. The dict has the following structure:
        {hash:subset}
        hash: The hash of the subset.
        subset: The bytes object corresponding to the hash."""
        fletcher_space = 65536
        hash_values = list(range(1, fletcher_space + 1))
        hash_frequencies = list()
        for integer in range(1, fletcher_space + 1):
            hash_frequencies.append(0)
        chunks = self.gen_chunks(file_pointer, chunk_size)
        for chunk in chunks:
            hashes = self.gen_chunk_hashes(chunk)
            for _hash in hashes:
                subset = chunk[_hash.start:_hash.end]
                try:
                    hash_values[_hash.hash].add(subset)
                except AttributeError:
                    hash_values[_hash.hash] = set(subset)
                hash_frequencies[_hash.hash] += 1
        return (hash_values, hash_frequencies)

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
            hashes (dict): The hashes for each distinct subset in the chunk as
            keys with their frequencies as values.
        """
        file_pointer = open(filepath, 'rb')
        fp = file_pointer
        frequencies = self.create_hash_table(fp, chunk_size)
        chunks = tuple(self.gen_file_chunks(fp, chunk_size))
        # This will just give the full filepath if we're on windows.
        return self.InputFile(fp.name.split("/")[-1], file_type, frequencies, chunks) 

    def list_hashes_by_frequency(self, hash_table):
        """Convert hash dict into a list so that it can be sorted and displayed
        in descending order with the most frequent hash at the top."""
        hash_list = hash_table[1]
        hash_list.sort(key=(lambda a: a[1]))
        hash_list.reverse()
        return hash_list

if __name__ == '__main__':
    main()
