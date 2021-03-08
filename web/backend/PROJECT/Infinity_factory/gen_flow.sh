
#!/bin/bash
#

outfile="Infinity_MLK_flow.xml"
cmd_list="sshcommand"
num=$(wc -l "$cmd_list" | awk '{print $1}')

# Generate XML header
cat xml_header.txt > "$outfile"


# Generate Test Case in Stage TN
echo "        <TestStage log_name=\"PRI\" stage=\"TN\">" >> "$outfile"
echo >> "$outfile"
for (( i=2 ; i<=$num ; i=i+1 ))
do
    testCase=$(awk -F "," -v r=$i 'NR==r {print $1}' "$cmd_list")
    command=$(awk -F "," -v r=$i 'NR==r {print $2}' "$cmd_list")
    timeout=$(awk -F "," -v r=$i 'NR==r {print $3}' "$cmd_list")
    err_code=$(awk -F "," -v r=$i 'NR==r {print $4}' "$cmd_list")
    type=$(awk -F "," -v r=$i 'NR==r {print $5}' "$cmd_list")

    echo "            <TestCase name=\""$testCase"\">" >> "$outfile"

    if [ "$type" -eq 0 ];
    then
        echo "                <Cmd>"$command"</Cmd>" >> "$outfile"
    elif [ "$type" -eq 1 ];
    then
        echo "                <SSHCmd>"$command"</SSHCmd>" >> "$outfile"
    fi

    echo "                <Timeout>"$timeout"</Timeout>" >> "$outfile"
    echo "                <ErrCode>"$err_code"</ErrCode>" >> "$outfile"
    echo "            </TestCase>" >> "$outfile"
    echo >> "$outfile"
done
echo "        </TestStage>" >> "$outfile"


# Generate Test Case in Stage TO


# Generate XML tailer
cat xml_tailer.txt >> "$outfile"

