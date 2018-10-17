import argparse
import subprocess


def patch_collector(dir_path, author, output):
    print(f'\n**Inside {dir_path}**\n')
    end = ''
    begin = ''
    patch_count = 1
    range_count = 1

    get_hashes_cmd = (f'git -C {dir_path} log --pretty=format:"%h" '
                      f'--author={author}')
    hashes = subprocess.check_output(get_hashes_cmd, shell=True)
    hashes = hashes.decode(encoding='utf-8')
    hashes = hashes.split('\n')

    for hash in hashes:

        ancestor_hash_cmd = (f'git -C {dir_path} log --pretty=format:"%h" '
                             f'--author={author} {hash}^^..{hash}^ --exit-code'
                             ' 1>/dev/null')

        if subprocess.Popen(ancestor_hash_cmd, shell=True).wait():
            if end == "":
                end = hash
            begin = hash
            range_count = range_count + 1

        else:
            subdir_msg = ('\nPlease enter a subdirectory name for this patch'
                          '(leave this empty\nto leave this patch out, use ./ '
                          'for the root directory):')
            print('\n')

            if end == "":
                temp = patch_count-1
                print(f'Adding one patch to {temp} existing:')
                subprocess.Popen(
                    f'git -C {dir_path} log {hash}^..{hash}', shell=True) \
                    .wait()
                print(subdir_msg)
                subdir = input()

                if subdir != '':
                    subprocess.Popen(
                        f'mkdir -p {output}/{subdir}', shell=True).wait()
                    subprocess.Popen(
                        f'git -C {dir_path} format-patch {hash}^..{hash} -o '
                        f'{output}/{subdir}', shell=True).wait()
                    patch_count = patch_count + 1

                else:
                    print('Omitting patch...')

            else:
                temp = patch_count-1
                print(f'Adding {range_count} patches to {temp} existing')
                subprocess.Popen(
                    f'git -C {dir_path} log {begin}^^..{end} --oneline',
                    shell=True).wait()
                print(subdir_msg)
                subdir = input()

                if subdir != '':
                    print(f'mkdir -p {output}/{subdir}')
                    subprocess.Popen(
                        f'mkdir -p {output}/{subdir}', shell=True).wait()
                    subprocess.Popen(
                        f'git -C {dir_path} format-patch {begin}^^..{end} '
                        f'-o{output}/{subdir}', shell=True).wait()
                    patch_count = patch_count + range_count

                else:
                    print('Omitting patch series...')

                end = ""
                range_count = 1


def main():
    help_message = """This is a simple helper script that allows collecting all
        patches from one author in a git repository. It will detect consequent
        ranges of patches and ask for each range for a subdirectory so you can
        distinguish the patch series."""

    parser = argparse.ArgumentParser(description=help_message)
    parser.add_argument('author_name', help='Name of contributor')
    parser.add_argument('output_root_dir', help='Output directory path')
    parser.add_argument('input_dir_paths',
                        help="Input directories separated by ','")
    args = parser.parse_args()
    author = args.author_name
    output = args.output_root_dir
    input_dirs = args.input_dir_paths
    input_dir_paths = input_dirs.split(',')

    for input_path in input_dir_paths:
        patch_collector(input_path, author, output)


if __name__ == '__main__':
    main()
