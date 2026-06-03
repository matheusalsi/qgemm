# Set Chipyard Conda env
```bash
source ./env.sh
```

# Gemmini Scala
In ``chipyard/generators/gemmini/chipyard/GemminiConfigs.scala``
```scala
class GemminiINT4RocketConfig extends Config(
  new gemmini.Int4GemminiConfig  ++                            // use Gemmini systolic array GEMM accelerator
  new freechips.rocketchip.rocket.WithNHugeCores(1) ++
  new chipyard.config.WithSystemBusWidth(128) ++
  new chipyard.config.AbstractConfig)
```

In ``chipyard/generators/gemmini/src/main/scala/gemmini/Configs.scala``
```scala
  val int4Config = GemminiArrayConfig[SInt, Float, Float](
    inputType  = SInt(8.W),
    weightType = SInt(8.W),

    // ACCUMULATOR MAIOR para evitar overflow
    accType = SInt(32.W),

    spatialArrayInputType  = SInt(4.W),
    spatialArrayWeightType = SInt(4.W),

    spatialArrayOutputType = SInt(20.W),

    tileRows = 1,
    tileColumns = 1,
    meshRows = 16,
    meshColumns = 16,

    dataflow = Dataflow.BOTH,

    sp_capacity  = CapacityInKilobytes(256),
    acc_capacity = CapacityInKilobytes(64),

    sp_banks = 4,
    acc_banks = 2,
    acc_sub_banks = 1,

    sp_singleported  = true,
    acc_singleported = false,

    has_training_convs = true,
    has_max_pool = true,
    has_nonlinear_activations = true,

    reservation_station_entries_ld = 8,
    reservation_station_entries_st = 4,
    reservation_station_entries_ex = 16,

    ld_queue_length = 8,
    st_queue_length = 2,
    ex_queue_length = 8,

    max_in_flight_mem_reqs = 16,

    dma_maxbytes = 64,
    dma_buswidth = 128,

    tlb_size = 4,

    mvin_scale_args = Some(ScaleArguments(
      (t: SInt, f: Float) => {
        val scaled = (t.asSInt * f.asUInt.asSInt)
        val maxsat = 7.S   // INT4 signed → -8 a +7
        val minsat = (-8).S
        Mux(scaled > maxsat, maxsat,
          Mux(scaled < minsat, minsat, scaled))
      },
      4, Float(8, 24), 4,
      identity = "1.0",
      c_str = "({float y = (x)*(scale); y > 7 ? 7 : (y < -8 ? -8 : (int)y);})"
    )),

    acc_scale_args = Some(ScaleArguments(
      (t: SInt, f: Float) => {
        val f_rec = recFNFromFN(f.expWidth, f.sigWidth, f.bits)

        val in_to_rec_fn = Module(new INToRecFN(t.getWidth, f.expWidth, f.sigWidth))
        in_to_rec_fn.io.signedIn := true.B
        in_to_rec_fn.io.in := t.asTypeOf(UInt(t.getWidth.W))
        in_to_rec_fn.io.roundingMode := consts.round_near_even
        in_to_rec_fn.io.detectTininess := consts.tininess_afterRounding

        val t_rec = in_to_rec_fn.io.out

        val muladder = Module(new MulAddRecFN(f.expWidth, f.sigWidth))
        muladder.io.op := 0.U
        muladder.io.roundingMode := consts.round_near_even
        muladder.io.detectTininess := consts.tininess_afterRounding

        muladder.io.a := t_rec
        muladder.io.b := f_rec
        muladder.io.c := 0.U

        val rec_fn_to_in = Module(new RecFNToIN(f.expWidth, f.sigWidth, t.getWidth))
        rec_fn_to_in.io.in := muladder.io.out
        rec_fn_to_in.io.roundingMode := consts.round_near_even
        rec_fn_to_in.io.signedOut := true.B

        val overflow = rec_fn_to_in.io.intExceptionFlags(1)

        // ACC ainda é 32 bits → saturação normal de int32
        val maxsat = ((1 << (t.getWidth-1))-1).S
        val minsat = (-(1 << (t.getWidth-1))).S

        val sign = rawFloatFromRecFN(f.expWidth, f.sigWidth, rec_fn_to_in.io.in).sign
        val sat = Mux(sign, minsat, maxsat)

        Mux(overflow, sat, rec_fn_to_in.io.out.asTypeOf(t))
      },
      8, Float(8, 24), -1,   // ⚠️ ESSA LATÊNCIA NÃO PODE SER ZERO
      identity = "1.0",
      c_str = "({float y = ROUND_NEAR_EVEN((x) * (scale)); y > INT32_MAX ? INT32_MAX : (y < INT32_MIN ? INT32_MIN : (acc_t)y);})"
    )),

    mvin_scale_shared = false,

    num_counter = 8,

    acc_read_full_width = true,
    acc_read_small_width = true,

    ex_read_from_spad = true,
    ex_read_from_acc  = true,
    ex_write_to_spad = true,
    ex_write_to_acc  = true
  )

class Int4GemminiConfig extends Config(
  new DefaultGemminiConfig(GemminiConfigs.int4Config)
)
```

# Functional Simulation

Navigate to the desired simulator directory (`verilator`, `vcs`, or `xcelium`):

```bash
cd chipyard/sims/<simulator>
make CONFIG=GemminiRocketConfig run-binary BINARY=../../generators/gemmini/software/gemmini-rocc-tests/build/imagenet/resnet50-baremetal TIMEOUT_CYCLES=0 LOADMEM=1
```

# VLSI FLOW
## Enviroment Setup
Substitua <pdk> por sky130 ou asap7

```bash
cd chipyard/scripts
./init-vlsi.sh <pdk>
```
## VLSI Flow Setup
In ``chipyard/vlsi/``, edit the ``env.yml`` to setup commercial tools.
```yml
# Base path to where Mentor tools are installed
mentor.mentor_home: ""
# Mentor license server/file
mentor.MGLS_LICENSE_FILE: ""
# Base path to where Cadence tools are installed
cadence.cadence_home: "/tools/cadence"
# Cadence license server/file
cadence.CDS_LIC_FILE: "5280@pgmicro01.ufrgs.br:27010@pgmicro01.ufrgs.br"
# Base path to where Synopsys tools are installed
synopsys.synopsys_home: ""
# Synopsys license server/files
synopsys.SNPSLMD_LICENSE_FILE: ""
synopsys.MGLS_LICENSE_FILE: ""
```

### Tools YML Examples
- OpenRoad in ``example-openroad.yml``
```yml
synthesis.yosys.yosys_bin: /home/inf01185/matheus.almeida/.conda-yosys/bin/yosys
par.openroad.openroad_bin: /home/inf01185/matheus.almeida/.conda-openroad/bin/openroad
par.openroad.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.klayout.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.magic.magic_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/magic
lvs.netgen.netgen_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/netgen
```

- Cadence Tools in ``example-tools.yml``
```yml
synthesis.yosys.yosys_bin: /home/inf01185/matheus.almeida/.conda-yosys/bin/yosys
par.openroad.openroad_bin: /home/inf01185/matheus.almeida/.conda-openroad/bin/openroad
par.openroad.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.klayout.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.magic.magic_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/magic
lvs.netgen.netgen_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/netgen
```
### PDK YML Example
To setup SKY130 PDK, go to ``example-sky130.yml`` and add the PDK paths.
```yml
# Technology paths
technology.sky130:
  sky130A: "/pdk/skywater/sky130/sky130A/"
  sram22_sky130_macros: "/home/inf01185/matheus.almeida/sram22_sky130_macros"
```

## VLSI Flow Run
```bash
make buildfile tutorial=sky130-commercial tech_name=sky130
make syn tutorial=sky130-commercial tech_name=sky130
make par tutorial=sky130-commercial tech_name=sky130

```

