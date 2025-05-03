# THX Spatial Audio+ Enhancements for AutoEq

ACCESS: branch of public fork of Jaakko Pasanen's [AutoEq](https://github.com/jaakkopasanen/AutoEq.git), available under an [MIT license](https://github.com/jaakkopasanen/AutoEq/blob/master/LICENSE).

## THX Spatial Audio+

[THX Spatial Audio+](https://www.thx.com/spatial-audio/) is a re-write of audio processing technologies designed to enhance stereo and surround sound, to deliver next-generation audio that intensifies 3D soundscapes in all forms of entertainment.

Partner products that make use of these technologies on Microsoft Windows platforms implement audio processing as a Windows driver-resident [Audio Processing Object](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/audio-processing-object-architecture).

Stereo headphones and gaming headsets directly supported by **THX APO 4** on Windows platforms are measured on a variety of IEC60318-4 compliant fixtures in our global testing laboratories, analyzing everything from output level, frequency response, signal-to-noise, and distortion to recreate high-impact, immersive sound and best-in-class audio fidelity.

## Transducer Compensation Equalization

**THX Spatial Audio+** provides a multi-function equalization block, on a per-device basis, which can be used to normalize frequency response to a response curve originally described in a 2013 AES research paper, [Listener Preference For Different Headphone Target Response Curves](https://www.researchgate.net/publication/287536305_Listener_preference_for_different_headphone_target_response_curves), by **Sean E. Olive**, **Todd Welti**, and **Elisabeth McMullin** from Harman International's Northridge, CA labs.

THX has standardized upon the **Harman AE/OE 2018 Target** curve as described in the follow-up research paper, [A Statistical Model that Predicts Listeners’ Preference Ratings of Around-Ear and On-Ear Headphones](https://aes2.org/publications/elibrary-page/?id=19436), by **Sean E. Olive**, **Todd Welti**, and **Omid Khonsaripour**.

>TODO - clarify level of additional bass boost in dB, noting that the AutoEq default is +6.0 dB at 105 Hz, implemented as a low-shelf filter, for a total of 10 dB bass boost.

The ability to configure the available filter bands largely matches those available in other enthusiast audio equalization applications, such as Jonas Dahlinger's [EqualizerAPO](https://sourceforge.net/projects/equalizerapo/), or John Mulcahy's [Room EQ Wizard](https://www.roomeqwizard.com/), constrained for our purposes as follows:

- one (1) `LOW_SHELF` band
- eight (8) `PEAK`ing bands
- one (1) `HIGH_SHELF` band

>NOTE: To protect the confidentiality of our partners' as-yet unreleased products, the `../measurements/THX/` and `../results/THX/` paths are submoduled as internal repositories with private access for THX internal use.

---
`./docs/README.md`
