echo 'Removing the files on the C drive'
rm -rfv ./VOICE

echo 'Copy the files from the Sony voice Recorder, preserving the dates'
cp -rfva /e/VOICE ./

echo 'Removing meta files and empty folders'
rm ./VOICE/MSGLISTL.MSF
rmdir -v --ignore-fail-on-non-empty ./VOICE/*

echo 'Summary of copied files'
du -h ./VOICE
