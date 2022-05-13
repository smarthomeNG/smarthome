# SMA-EM Plugin

This plugin retrieves the data sent by the SMA Energy Meter.
In agreement with the author Florian Wenger, this plugin uses code published in
https://github.com/datenschuft/SMA-EM/ - especially the readem method.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/1030610-sma_em-plugin

The SMA Energy Meter broadcasts its information via multicast to the network address 239.12.255.254. Beyond the items
supported by this plugin, the readem method allows for a lot more of parameters. The items will be extended in future
versions of this plugin on demand. The available values can be seen in the readem method of this plugin.

If demand exists, the plugin can also be extended to be used with more than one energy meter.

The new version of the Plugin has been completely adapted to the changes in the datagram as documented in http://www.eb-systeme.de/?page_id=3005.

## Configuration

### plugin.yaml

```yaml
sma_em:
    class_name: SMA_EM
    class_path: plugins.sma_em
    serial: xxxxxxxxxx
    cycle: 5
```

#### Attributes
  * `serial`: The serial number of your energy meter
  * `cycle`: The time in seconds to wait after a multicast was received. I introduced this to avoid too many values to be processed.

### items.yaml

#### Example:

```yaml
smaem:
    main:
        name: Main Data from SMA Energy Meter

        speedwire_version:
            name: Speedwire Version
            sma_em_data_type: speedwire-version
            type: str

        supply:
            name: Solar Energy Supply
            sma_em_data_type: psupply
            type: num

            kw:
                type: num
                eval: round(sh...() / 1000, 2)
                eval_trigger: ..

        supply_unit:
            name: Solar Energy Supply Unit
            sma_em_data_type: psupplyunit
            type: str

        consume:
            name: Solar Energy Consume
            sma_em_data_type: pconsume
            type: num

            kw:
                type: num
                eval: round(sh...() / 1000, 2)
                eval_trigger: ..

        consume_unit:
            name: Solar Energy Consume Unit
            sma_em_data_type: pconsumeunit
            type: str

        supply_counter:
            name: Solar Energy Supply Counter
            sma_em_data_type: psupplycounter
            type: num

        supply_counter_unit:
            name: Solar Energy Supply Counter Unit
            sma_em_data_type: psupplycounterunit
            type: str

        consume_counter:
            name: Solar Energy Consume Counter
            sma_em_data_type: pconsumecounter
            type: num

        consume_counter_unit:
            name: Solar Energy Consume Counter Unit
            sma_em_data_type: pconsumecounterunit
            type: str

        cosphi:
            sma_em_data_type: cosphi
            type: num

        cosphi_unit:
            sma_em_data_type: cosphiunit
            type: str

        consume_active:
            type: bool
            eval: True if sh...consume() > 1 else False
            eval_trigger: ..consume

        supply_active:
            type: bool
            eval: True if sh...supply() > 1 else False
            eval_trigger: ..supply

    detailed:
        name: More Detailed Data from SMA Energy Meter

        ssupply:
            sma_em_data_type: ssupply
            type: num

        ssupply_unit:
            sma_em_data_type: ssupplyunit
            type: str

        ssupply_counter:
            sma_em_data_type: ssupplycounter
            type: num

        ssupply_counter_unit:
            sma_em_data_type: ssupplycounterunit
            type: str

        sconsume:
            sma_em_data_type: sconsume
            type: num

        sconsume_unit:
            sma_em_data_type: sconsumeunit
            type: str

        sconsume_counter:
            sma_em_data_type: sconsumecounter
            type: num

        sconsume_counter_unit:
            sma_em_data_type: sconsumecounterunit
            type: str

        qsupply:
            sma_em_data_type: qsupply
            type: num

        qsupply_unit:
            sma_em_data_type: qsupplyunit
            type: str

        qsupply_counter:
            sma_em_data_type: qsupplycounter
            type: num

        qsupply_counter_unit:
            sma_em_data_type: qsupplycounterunit
            type: str

        qconsume:
            sma_em_data_type: qconsume
            type: num

        qconsume_unit:
            sma_em_data_type: qconsumeunit
            type: str

        qconsume_counter:
            sma_em_data_type: qconsumecounter
            type: num

        qconsume_counter_unit:
            sma_em_data_type: qconsumecounterunit
            type: str

        p1supply:
            sma_em_data_type: p1supply
            type: num

        p1supply_unit:
            sma_em_data_type: p1supplyunit
            type: str

        p1supply_counter:
            sma_em_data_type: p1supplycounter
            type: num

        p1supply_counter_unit:
            sma_em_data_type: p1supplycounterunit
            type: str

        p1consume:
            sma_em_data_type: p1consume
            type: num

        p1consume_unit:
            sma_em_data_type: p1consumeunit
            type: str

        p1consume_counter:
            sma_em_data_type: p1consumecounter
            type: num

        p1consume_counter_unit:
            sma_em_data_type: p1consumecounterunit
            type: str

        s1supply:
            sma_em_data_type: s1supply
            type: num

        s1supply_unit:
            sma_em_data_type: s1supplyunit
            type: str

        s1supply_counter:
            sma_em_data_type: s1supplycounter
            type: num

        s1supply_counter_unit:
            sma_em_data_type: s1supplycounterunit
            type: str

        s1consume:
            sma_em_data_type: s1consume
            type: num

        s1consume_unit:
            sma_em_data_type: s1consumeunit
            type: str

        s1consume_counter:
            sma_em_data_type: s1consumecounter
            type: num

        s1consume_counter_unit:
            sma_em_data_type: s1consumecounterunit
            type: str

        q1supply:
            sma_em_data_type: q1supply
            type: num

        q1supply_unit:
            sma_em_data_type: q1supplyunit
            type: str

        q1supply_counter:
            sma_em_data_type: q1supplycounter
            type: num

        q1supply_counter_unit:
            sma_em_data_type: q1supplycounterunit
            type: str

        q1consume:
            sma_em_data_type: q1consume
            type: num

        q1consume_unit:
            sma_em_data_type: q1consumeunit
            type: str

        q1consume_counter:
            sma_em_data_type: q1consumecounter
            type: num

        q1consume_counter_unit:
            sma_em_data_type: q1consumecounterunit
            type: str

        i1:
            sma_em_data_type: i1
            type: num

        i1_unit:
            sma_em_data_type: i1unit
            type: str

        u1:
            sma_em_data_type: u1
            type: num

        u1_unit:
            sma_em_data_type: u1unit
            type: str

        cosphi1:
            sma_em_data_type: cosphi1
            type: num

        cosphi1_unit:
            sma_em_data_type: cosphi1unit
            type: str

        p2supply:
            sma_em_data_type: p2supply
            type: num

        p2supply_unit:
            sma_em_data_type: p2supplyunit
            type: str

        p2supply_counter:
            sma_em_data_type: p2supplycounter
            type: num

        p2supply_counter_unit:
            sma_em_data_type: p2supplycounterunit
            type: str

        p2consume:
            sma_em_data_type: p2consume
            type: num

        p2consume_unit:
            sma_em_data_type: p2consumeunit
            type: str

        p2consume_counter:
            sma_em_data_type: p2consumecounter
            type: num

        p2consume_counter_unit:
            sma_em_data_type: p2consumecounterunit
            type: str

        s2supply:
            sma_em_data_type: s2supply
            type: num

        s2supply_unit:
            sma_em_data_type: s2supplyunit
            type: str

        s2supply_counter:
            sma_em_data_type: s2supplycounter
            type: num

        s2supply_counter_unit:
            sma_em_data_type: s2supplycounterunit
            type: str

        s2consume:
            sma_em_data_type: s2consume
            type: num

        s2consume_unit:
            sma_em_data_type: s2consumeunit
            type: str

        s2consume_counter:
            sma_em_data_type: s2consumecounter
            type: num

        s2consume_counter_unit:
            sma_em_data_type: s2consumecounterunit
            type: str

        q2supply:
            sma_em_data_type: q2supply
            type: num

        q2supply_unit:
            sma_em_data_type: q2supplyunit
            type: str

        q2supply_counter:
            sma_em_data_type: q2supplycounter
            type: num

        q2supply_counter_unit:
            sma_em_data_type: q2supplycounterunit
            type: str

        q2consume:
            sma_em_data_type: q2consume
            type: num

        q2consume_unit:
            sma_em_data_type: q2consumeunit
            type: str

        q2consume_counter:
            sma_em_data_type: q2consumecounter
            type: num

        q2consume_counter_unit:
            sma_em_data_type: q2consumecounterunit
            type: str

        i2:
            sma_em_data_type: i2
            type: num

        i2_unit:
            sma_em_data_type: i2unit
            type: str

        u2:
            sma_em_data_type: u2
            type: num

        u2_unit:
            sma_em_data_type: u2unit
            type: str

        cosphi2:
            sma_em_data_type: cosphi2
            type: num

        cosphi2_unit:
            sma_em_data_type: cosphi2unit
            type: str

        p3supply:
            sma_em_data_type: p3supply
            type: num

        p3supply_unit:
            sma_em_data_type: p3supplyunit
            type: str

        p3supply_counter:
            sma_em_data_type: p3supplycounter
            type: num

        p3supply_counter_unit:
            sma_em_data_type: p3supplycounterunit
            type: str

        p3consume:
            sma_em_data_type: p3consume
            type: num

        p3consume_unit:
            sma_em_data_type: p3consumeunit
            type: str

        p3consume_counter:
            sma_em_data_type: p3consumecounter
            type: num

        p3consume_counter_unit:
            sma_em_data_type: p3consumecounterunit
            type: str

        s3supply:
            sma_em_data_type: s3supply
            type: num

        s3supply_unit:
            sma_em_data_type: s3supplyunit
            type: str

        s3supply_counter:
            sma_em_data_type: s3supplycounter
            type: num

        s3supply_counter_unit:
            sma_em_data_type: s3supplycounterunit
            type: str

        s3consume:
            sma_em_data_type: s3consume
            type: num

        s3consume_unit:
            sma_em_data_type: s3consumeunit
            type: str

        s3consume_counter:
            sma_em_data_type: s3consumecounter
            type: num

        s3consume_counter_unit:
            sma_em_data_type: s3consumecounterunit
            type: str

        q3supply:
            sma_em_data_type: q3supply
            type: num

        q3supply_unit:
            sma_em_data_type: q3supplyunit
            type: str

        q3supply_counter:
            sma_em_data_type: q3supplycounter
            type: num

        q3supply_counter_unit:
            sma_em_data_type: q3supplycounterunit
            type: str

        q3consume:
            sma_em_data_type: q3consume
            type: num

        q3consume_unit:
            sma_em_data_type: q3consumeunit
            type: str

        q3consume_counter:
            sma_em_data_type: q3consumecounter
            type: num

        q3consume_counter_unit:
            sma_em_data_type: q3consumecounterunit
            type: str

        i3:
            sma_em_data_type: i3
            type: num

        i3_unit:
            sma_em_data_type: i3unit
            type: str

        u3:
            sma_em_data_type: u3
            type: num

        u3_unit:
            sma_em_data_type: u3unit
            type: str

        cosphi3:
            sma_em_data_type: cosphi3
            type: num

        cosphi3_unit:
            sma_em_data_type: cosphi3unit
            type: str
```
