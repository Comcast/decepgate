FILE=/nvram/honeyd_tmp/demo.conf
if [ -f "$FILE" ]; then
    echo "$FILE exist"
    if pidof  "honeyd"  > /dev/null;
    then
        echo "Running"
        PID=`pidof honeyd`
        kill -9 $PID
        sleep 15
        if pidof  "honeyd" > /dev/null;
        then
            PID=`pidof honeyd`
            echo "Still running"
            echo $PID
        else
            echo "Restart honeyd"
            read -r command < /tmp/honeyd_tmp/demo.conf
            mkdir -p /nvram/honeyd_conf
            cp /tmp/honeyd_tmp/demo.conf /tmp/honeyd_conf
            sed -i "1,1 d" /tmp/honeyd_conf/demo.conf
            $command &
        fi
    else
        echo "Start services"
        read -r command < /tmp/honeyd_tmp/demo.conf
        mkdir -p /tmp/honeyd_conf
        cp /tmp/honeyd_tmp/demo.conf /tmp/honeyd_conf
        sed -i "1,1 d" /tmp/honeyd_conf/demo.conf
	sleep 5
        $command &
    fi
else 
    echo "$FILE does not exist"
fi

