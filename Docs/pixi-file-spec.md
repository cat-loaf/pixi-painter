# PIXI File Format v1 
## Flags Enumeration
| Flag Value | Description                | 
| ---------- | -------------------------- |
| (0x00)     | No Flags (Assume Defaults) |
| (0x?1)     | RGB                        |
| (0x?2)     | RGBA                       |
| (0x?3)     | CMYK                       |
| (0x?4)     | CMYKA                      |
| (0x?5)     | Indexed Colours            |
| (0x1?)     | Is Compressed              |

## Header Data
| Location | Size | Description | 
| - | - | - |
| 0x00 | 4 bytes | magic number 0x50495849 (PIXI in ASCII) |
| 0x04 | 2 bytes | major version 0x00 |
| 0x06 | 2 bytes | minor version 0x01 |
| 0x08 | 4 bytes | width of image |
| 0x0C | 4 bytes | height of image |
| 0x10 | 1 byte  | flags |
| 0x11 | 1 byte  | triplet size (3 = RGB, 4 = RGBA, 4 = CYMK, 5 = CMYKA) |
| 0x12 | 2 bytes | reserved |

## File Metadata
| Location | Size | Description | 
| - | - | - |
| 0x14       | 4 bytes   | length of creator name |
| 0x1B       | i bytes   | creator name |
| 0x1B+i     | 4 bytes   | length of description |
| 0x1F+i     | j bytes   | description |
| 0x1F+i+j   | 4 bytes   | length of tags/keywords |
| 0x23+i+j   | k bytes   | tags/keywords |
| 0x23+i+j+k | 126 bytes | checksum |

## Image Data
| Location | Size | Description | 
| - | - | - |
| 0xA1+i+j+k   | 4 bytes | indexed colours amount |
| 0xA5+i+j+k   | l bytes | colour palette (indexed colours) |
| 0xA5+i+j+k+l | m bytes | image data     (amount to read = width * height * triplet size) |


